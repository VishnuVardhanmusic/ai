import litellm
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from prompt_manager import buildPrompt

def runReview(prompt, model="ollama/llama3", max_tokens=2048):
    """
    Sends the prompt to the specified LLM using LiteLLM and returns JSON feedback.
    """
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=max_tokens
        )
        output = response['choices'][0]['message']['content']

        # Extract first valid JSON array
        json_match = re.search(r'\[\s*{.*?}\s*\]', output, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            print("❌ Could not extract valid JSON array from LLM response.")
            print("📝 Raw Output:\n", output)
            return []

    except json.JSONDecodeError:
        print("❌ LLM response was not valid JSON.")
        print("📝 Response:\n", output)
        return []
    except Exception as e:
        print("❌ Error calling model:", str(e))
        return []

def runParallelReviews(code_lines, guideline_chunks, model="ollama/llama3"):
    """
    Runs multiple LLM reviews in parallel using guideline chunks.

    Args:
        code_lines (list): Parsed source code lines.
        guideline_chunks (list): List of guideline subsets (per agent).
        model (str): Model identifier.

    Returns:
        list: Merged review results from all agents.
    """
    results = []

    def agent_task(chunk):
        prompt = buildPrompt(code_lines, chunk)
        return runReview(prompt, model=model)

    with ThreadPoolExecutor(max_workers=len(guideline_chunks)) as executor:
        future_to_chunk = {executor.submit(agent_task, chunk): chunk for chunk in guideline_chunks}
        for future in as_completed(future_to_chunk):
            try:
                result = future.result()
                results.extend(result)
            except Exception as e:
                print(f"❌ Agent failed with error: {str(e)}")

    # Optional: Deduplicate violations (based on line + rule ID)
    unique_reviews = []
    seen = set()
    for item in results:
        key = (item.get("lineNumber"), item.get("ruleViolated"))
        if key not in seen:
            unique_reviews.append(item)
            seen.add(key)

    return unique_reviews

def saveReviewToFile(reviewData, outputPath="code_review.json"):
    """
    Saves the final review remarks to a JSON file.
    """
    with open(outputPath, 'w') as f:
        json.dump(reviewData, f, indent=4)
    print(f"✅ Review saved to: {outputPath}")


def extract_json_array(text):
    start = text.find("[")
    if start == -1:
        return None

    array_str = ""
    current_obj = ""
    brace_count = 0
    inside_array = False
    valid_objects = []

    for char in text[start:]:
        array_str += char

        if char == "{":
            brace_count += 1
            current_obj += char
        elif char == "}":
            brace_count -= 1
            current_obj += char

            if brace_count == 0:
                # Complete JSON object
                try:
                    obj = json.loads(current_obj)
                    valid_objects.append(obj)
                except:
                    pass  # Skip invalid object
                current_obj = ""
        elif brace_count > 0:
            current_obj += char

    return valid_objects if valid_objects else None

##########################################################
        def extract_json_array(text):
            start = text.find("[")
            if start == -1:
                return []

            array_str = ""
            current_obj = ""
            brace_count = 0
            inside_array = False
            valid_objects = []

            for char in text[start:]:
                array_str += char

                if char == "{":
                    brace_count += 1
                    current_obj += char
                elif char == "}":
                    brace_count -= 1
                    current_obj += char

                    if brace_count == 0:
                        # Try loading complete JSON object
                        try:
                            obj = json.loads(current_obj)
                            valid_objects.append(obj)
                        except:
                            pass
                        current_obj = ""
                elif brace_count > 0:
                    current_obj += char

            return valid_objects  # returns [] if no objects parsed

        parsed = extract_json_array(output)
        return parsed if isinstance(parsed, list) else []

    except Exception as e:
        print("❌ Error during LLM review:", str(e))
        return []