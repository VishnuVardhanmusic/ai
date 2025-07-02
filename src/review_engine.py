def runReview(prompt, model="ollama/llama3", max_tokens=2048):
    """
    Sends the prompt to the specified LLM using LiteLLM and returns JSON feedback.
    Gracefully handles incomplete or malformed JSON arrays.
    """
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=max_tokens
        )
        output = response['choices'][0]['message']['content']

        # --- Robust JSON Array Extraction ---
        def extract_json_array(text):
            start = text.find("[")
            if start == -1:
                return None  # No JSON array found

            bracket_count = 0
            in_object = False
            array_str = ""

            for i in range(start, len(text)):
                char = text[i]
                array_str += char

                if char == "{":
                    in_object = True
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                elif char == "]" and bracket_count == 0 and in_object:
                    # likely end of array
                    break

            # Try parsing what we have
            try:
                return json.loads(array_str)
            except json.JSONDecodeError:
                # Try to clean up trailing commas and retry
                array_str = array_str.rstrip(", \n\r") + "]"
                try:
                    return json.loads(array_str)
                except:
                    return None

        parsed_json = extract_json_array(output)
        if parsed_json is not None:
            return parsed_json
        else:
            print("❌ Could not parse JSON array from model output.")
            print("📝 Raw Output:\n", output)
            return []

    except Exception as e:
        print("❌ Error calling model:", str(e))
        return []
