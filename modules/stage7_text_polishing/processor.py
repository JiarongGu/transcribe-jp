"""LLM-powered subtitle polishing"""

import json
from shared.llm_utils import create_llm_provider, parse_json_response


def polish_segments_with_llm(segments, config):
    """Use LLM to polish subtitle text for better formatting"""
    text_polishing_config = config.get("text_polishing", {})

    if not text_polishing_config.get("enable", False):
        return segments

    # Create LLM provider (with stage-specific config if available)
    llm_provider = create_llm_provider(config, stage_name="text_polishing")

    if not llm_provider:
        # LLM provider not available, skip polishing
        return segments

    try:
        # Get LLM config for parameters
        llm_config = config.get("llm", {})

        # Process in batches to reduce API calls
        # batch_size <= 1 means process one-by-one (useful for Ollama and other local providers)
        batch_size = text_polishing_config.get("batch_size", 10)
        polished_segments = []
        total_segments = len(segments)

        # If batch_size is 0 or 1, process one-by-one
        if batch_size <= 1:
            batch_size = 1
            print(f"  - Processing {total_segments} segments one-by-one (batch processing disabled)")
        else:
            total_batches = (len(segments) + batch_size - 1) // batch_size
            print(f"  - Processing {total_segments} segments in {total_batches} batches (batch size: {batch_size})")

        def _print_progress(completed, total):
            """Print progress bar"""
            percent = 100 * (completed / float(total))
            filled = int(40 * completed // total)
            bar = '█' * filled + '░' * (40 - filled)
            print(f'\r    Progress: |{bar}| {completed}/{total} ({percent:.0f}%)', end='', flush=True)
            if completed == total:
                print()  # New line on completion

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            batch_num = i // batch_size + 1

            # Track batch status for summary
            batch_success = False
            batch_error_msg = None
            one_by_one_success = 0

            # Extract texts for polishing
            texts = []
            for seg in batch:
                if len(seg) >= 3:
                    texts.append(seg[2])  # text is 3rd element
                else:
                    texts.append("")

            # Build prompt
            numbered_texts = "\n".join([f"{idx+1}. {text}" for idx, text in enumerate(texts)])

            prompt = f"""これは音声認識によって生成された日本語字幕です。実際に話された内容を書き起こしたものなので、話者が実際に言った通りに字幕を整形してください。

重要な注意事項:
- これは音声の書き起こしです。勝手に言葉を追加したり、話者が言っていないことを補完しないでください
- 話者が実際に話した内容を忠実に反映してください
- 口語表現や砕けた言い方はそのまま保持してください（話し言葉として自然です）

以下の最小限の修正のみを行ってください:
1. 明らかな音声認識エラーの修正（「わたし」→「私」など、同音異義語の誤変換のみ）
2. 文末に適切な句読点を追加（。？！など）
3. 不自然な区切りや改行を修正
4. 助詞の誤りを修正（「は」と「わ」、「を」と「お」など）

絶対にしないこと:
- 話者が言っていない言葉を追加しない
- 口語を書き言葉に変更しない（「〜だよ」「〜じゃん」「〜って感じ」などはそのまま）
- 言い直しや言い淀みを削除しない（それも話者の発言の一部です）

元のテキスト（音声認識結果）:
{numbered_texts}

JSON形式で返してください。例: {{"polished": ["整形後1", "整形後2", "整形後3"]}}
JSONのみ出力してください。説明や理由は不要です。"""

            try:
                # Generate response using provider
                max_tokens = llm_config.get("max_tokens", 1024)
                temperature = llm_config.get("temperature", 0.0)
                response_text = llm_provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)

                # Parse JSON response with context for error logging
                context = {
                    "stage": "text_polishing",
                    "batch_num": batch_num,
                    "batch_size": len(batch),
                    "total_segments": total_segments,
                    "processing_mode": "batch"
                }
                result = parse_json_response(response_text, prompt=prompt, context=context)

                # Handle both dict {"polished": [...]} and direct list [...]
                if isinstance(result, list):
                    polished_texts = result
                elif isinstance(result, dict):
                    polished_texts = result.get("polished", texts)
                    # Validate type - if not a list, use original texts
                    if not isinstance(polished_texts, list):
                        polished_texts = texts
                else:
                    polished_texts = texts

                # Replace texts in segments
                for j, polished_text in enumerate(polished_texts):
                    if j < len(batch):
                        seg = batch[j]
                        if len(seg) == 4:
                            # Preserve timing and words
                            polished_segments.append((seg[0], seg[1], polished_text, seg[3]))
                        elif len(seg) == 3:
                            polished_segments.append((seg[0], seg[1], polished_text))
                        else:
                            polished_segments.append(seg)

                batch_success = True

            except Exception as e:
                # Batch failed, try individually
                batch_error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                print(f"\r    Batch {batch_num} failed ({batch_error_msg})", flush=True)
                print(f"    Retrying {len(batch)} segments individually...", flush=True)

                # Try polishing one-by-one
                for j, seg in enumerate(batch):
                    if len(seg) >= 3:
                        text = seg[2]
                        try:
                            prompt = f"""これは音声認識によって生成された日本語字幕です。実際に話された内容を書き起こしたものなので、話者が実際に言った通りに字幕を整形してください。

重要な注意事項:
- これは音声の書き起こしです。勝手に言葉を追加したり、話者が言っていないことを補完しないでください
- 話者が実際に話した内容を忠実に反映してください
- 口語表現や砕けた言い方はそのまま保持してください（話し言葉として自然です）

以下の最小限の修正のみを行ってください:
1. 明らかな音声認識エラーの修正（「わたし」→「私」など、同音異義語の誤変換のみ）
2. 文末に適切な句読点を追加（。？！など）
3. 不自然な区切りや改行を修正
4. 助詞の誤りを修正（「は」と「わ」、「を」と「お」など）

絶対にしないこと:
- 話者が言っていない言葉を追加しない
- 口語を書き言葉に変更しない（「〜だよ」「〜じゃん」「〜って感じ」などはそのまま）
- 言い直しや言い淀みを削除しない（それも話者の発言の一部です）

元のテキスト（音声認識結果）:
1. {text}

JSON形式で返してください。例: {{"polished": ["整形後1"]}}
JSONのみ出力してください。説明や理由は不要です。"""

                            # Generate response using provider
                            max_tokens = llm_config.get("max_tokens", 1024)
                            temperature = llm_config.get("temperature", 0.0)
                            response_text = llm_provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)

                            # Parse JSON response with context for error logging
                            context = {
                                "stage": "text_polishing",
                                "batch_num": batch_num,
                                "segment_num": j + 1,
                                "total_in_batch": len(batch),
                                "processing_mode": "individual_retry",
                                "original_error": batch_error_msg,
                                "segment_text": text[:100]  # First 100 chars for reference
                            }
                            result = parse_json_response(response_text, prompt=prompt, context=context)

                            # Handle both dict {"polished": [...]} and direct list [...]
                            if isinstance(result, list):
                                polished_text = result[0] if result else text
                            elif isinstance(result, dict):
                                polished_list = result.get("polished", [text])
                                # Validate type - if not a list, use original text
                                if isinstance(polished_list, list):
                                    polished_text = polished_list[0] if polished_list else text
                                else:
                                    polished_text = text
                            else:
                                polished_text = text

                            # Add polished segment
                            if len(seg) == 4:
                                polished_segments.append((seg[0], seg[1], polished_text, seg[3]))
                            elif len(seg) == 3:
                                polished_segments.append((seg[0], seg[1], polished_text))
                            else:
                                polished_segments.append(seg)
                            one_by_one_success += 1

                        except Exception as e2:
                            # Keep original segment if one-by-one also fails
                            error_details = f"{type(e2).__name__}: {str(e2)[:100]}"
                            print(f"    WARNING: Segment {j+1}/{len(batch)} failed: {error_details}", flush=True)
                            print(f"             Text: {text[:80]}...", flush=True)
                            polished_segments.append(seg)
                    else:
                        # Keep segments without text unchanged
                        polished_segments.append(seg)

            # Update progress bar once per batch (after both success and failure paths)
            _print_progress(len(polished_segments), total_segments)

            # Print batch summary if there were failures
            if not batch_success:
                if one_by_one_success > 0:
                    print(f"    Batch {batch_num}: {one_by_one_success}/{len(batch)} segments succeeded in individual retry")
                else:
                    print(f"    Batch {batch_num}: All {len(batch)} segments failed (using original text)")

        print(f"  - Completed: {len(polished_segments)}/{total_segments} segments polished")
        return polished_segments

    except Exception as e:
        print(f"  - Warning: Polishing failed: {e}")
        return segments
