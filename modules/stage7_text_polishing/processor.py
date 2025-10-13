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

            # Extract texts for polishing
            texts = []
            for seg in batch:
                if len(seg) >= 3:
                    texts.append(seg[2])  # text is 3rd element
                else:
                    texts.append("")

            # Build prompt
            numbered_texts = "\n".join([f"{idx+1}. {text}" for idx, text in enumerate(texts)])

            prompt = f"""日本語字幕のテキストを整形してください。

以下のルールに従ってください:
1. 文末に適切な句読点を追加（。？！など）
2. 不自然な改行や区切りを修正
3. 助詞や語尾の不自然さを修正
4. 元の意味やニュアンスを保持
5. 口語的な表現はそのまま維持

元のテキスト:
{numbered_texts}

JSON形式で、整形後のテキストを配列で返してください。
例: {{"polished": ["整形後1", "整形後2", "整形後3"]}}

必ずJSONのみを返してください。説明文は不要です。"""

            try:
                # Generate response using provider
                max_tokens = llm_config.get("max_tokens", 1024)
                temperature = llm_config.get("temperature", 0.0)
                response_text = llm_provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)

                # Parse JSON response
                result = parse_json_response(response_text)
                polished_texts = result.get("polished", texts)

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

                # Update progress bar
                _print_progress(len(polished_segments), total_segments)

            except Exception as e:
                # Batch failed, try individually
                print(f"\r    Batch {batch_num} failed, retrying individually...", end="", flush=True)
                # Try polishing one-by-one
                one_by_one_success = 0
                for j, seg in enumerate(batch):
                    if len(seg) >= 3:
                        text = seg[2]
                        try:
                            prompt = f"""日本語字幕のテキストを整形してください。

以下のルールに従ってください:
1. 文末に適切な句読点を追加（。？！など）
2. 不自然な改行や区切りを修正
3. 助詞や語尾の不自然さを修正
4. 元の意味やニュアンスを保持
5. 口語的な表現はそのまま維持

元のテキスト:
1. {text}

JSON形式で、整形後のテキストを配列で返してください。
例: {{"polished": ["整形後1"]}}

必ずJSONのみを返してください。説明文は不要です。"""

                            # Generate response using provider
                            max_tokens = llm_config.get("max_tokens", 1024)
                            temperature = llm_config.get("temperature", 0.0)
                            response_text = llm_provider.generate(prompt, max_tokens=max_tokens, temperature=temperature)

                            # Parse JSON response
                            result = parse_json_response(response_text)
                            polished_text = result.get("polished", [text])[0]

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
                            polished_segments.append(seg)
                    else:
                        # Keep segments without text unchanged
                        polished_segments.append(seg)

                # Update progress bar after individual retry
                _print_progress(len(polished_segments), total_segments)
                if one_by_one_success > 0:
                    print(f"    ({one_by_one_success}/{len(batch)} succeeded in retry)")
                else:
                    print(f"    (batch failed)")

        print(f"  - Completed: {len(polished_segments)}/{total_segments} segments polished")
        return polished_segments

    except Exception as e:
        print(f"  - Warning: Polishing failed: {e}")
        return segments
