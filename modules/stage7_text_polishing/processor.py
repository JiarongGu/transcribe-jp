"""LLM-powered subtitle polishing"""

import os
import json


def polish_segments_with_llm(segments, config):
    """Use LLM to polish subtitle text for better formatting"""
    text_polishing_config = config.get("text_polishing", {})

    if not text_polishing_config.get("enable", False):
        return segments

    llm_config = config.get("llm", {})

    provider = llm_config.get("provider", "anthropic")
    if provider != "anthropic":
        return segments

    try:
        from anthropic import Anthropic

        # Get API key
        api_key = llm_config.get("anthropic_api_key") or os.environ.get(llm_config.get("api_key_env", "ANTHROPIC_API_KEY"))

        if not api_key:
            print(f"  - Warning: API key not found, skipping polishing")
            return segments

        client = Anthropic(api_key=api_key)

        # Process in batches to reduce API calls
        batch_size = text_polishing_config.get("batch_size", 10)
        polished_segments = []
        total_batches = (len(segments) + batch_size - 1) // batch_size
        total_segments = len(segments)

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
                message = client.messages.create(
                    model=llm_config.get("model", "claude-3-5-haiku-20241022"),
                    max_tokens=llm_config.get("max_tokens", 1024),
                    temperature=llm_config.get("temperature", 0.0),
                    messages=[{"role": "user", "content": prompt}]
                )

                response_text = message.content[0].text.strip()

                # Parse JSON response - handle markdown code blocks
                if response_text.startswith("```"):
                    lines = response_text.split('\n')
                    json_lines = []
                    in_code_block = False
                    for line in lines:
                        if line.startswith("```"):
                            in_code_block = not in_code_block
                            continue
                        if in_code_block or (not line.startswith("```") and json_lines):
                            json_lines.append(line)
                    response_text = '\n'.join(json_lines).strip()

                result = json.loads(response_text)
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

                            message = client.messages.create(
                                model=llm_config.get("model", "claude-3-5-haiku-20241022"),
                                max_tokens=llm_config.get("max_tokens", 1024),
                                temperature=llm_config.get("temperature", 0.0),
                                messages=[{"role": "user", "content": prompt}]
                            )

                            response_text = message.content[0].text.strip()

                            # Parse JSON response - handle markdown code blocks
                            if response_text.startswith("```"):
                                lines = response_text.split('\n')
                                json_lines = []
                                in_code_block = False
                                for line in lines:
                                    if line.startswith("```"):
                                        in_code_block = not in_code_block
                                        continue
                                    if in_code_block or (not line.startswith("```") and json_lines):
                                        json_lines.append(line)
                                response_text = '\n'.join(json_lines).strip()

                            result = json.loads(response_text)
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

    except ImportError:
        print(f"  - Warning: anthropic package not installed, skipping polishing")
        return segments
    except Exception as e:
        print(f"  - Warning: Polishing failed: {e}")
        return segments
