import os
import json
import re
import openai
import pyautogui
import cv2
import numpy as np

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise ValueError("Please set your OPENAI_API_KEY environment variable.")

# The provided tool function which executes a given command.
def computeruse_tool(args: dict) -> str:
    command_str = args.get("command", "")
    return f"Computer action executed: {command_str}"

# Function that sends the natural language task to the LLM and returns a structured JSON plan.
def send_to_llm(natural_language_task: str) -> dict:
    prompt = f"""You are a computer agent that receives a natural language task and returns a structured JSON plan for interacting with the desktop environment.
The JSON must have the following keys:
- "screenshot": a boolean value indicating whether to capture a screenshot.
- "visual_grounding": a boolean value indicating whether to perform visual grounding on the screenshot.
- "command": a string containing the command to execute.

Return only a valid JSON object.
Example:
{{
  "screenshot": true,
  "visual_grounding": true,
  "command": "click button at (100, 200)"
}}

The natural language task is:
"{natural_language_task}"
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts natural language tasks into structured JSON plans."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
    )
    structured_plan = response["choices"][0]["message"]["content"]
    try:
        plan = json.loads(structured_plan)
    except json.JSONDecodeError as e:
        print("Error decoding JSON from LLM response:", e)
        print("LLM response:", structured_plan)
        plan = {}
    return plan


def capture_screenshot() -> str:
    screenshot = pyautogui.screenshot()
    screenshot_path = "current_ui.png"
    screenshot.save(screenshot_path)
    print("Screenshot captured and saved as", screenshot_path)
    return screenshot_path


def perform_visual_grounding(screenshot_path: str) -> dict:
    print("Performing visual grounding on:", screenshot_path)
    image = cv2.imread(screenshot_path)
    if image is None:
        print("Error loading image for visual grounding.")
        return {}
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)
    

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_elements = {"buttons": [], "menus": [], "input_fields": []}
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if w < 30 or h < 30:
            continue
        
        aspect_ratio = w / float(h)

        if 0.8 < aspect_ratio < 1.2:
            detected_elements["buttons"].append((x, y, w, h))
            label = "Button"

        elif aspect_ratio > 2.5:
            detected_elements["menus"].append((x, y, w, h))
            label = "Menu"

        elif aspect_ratio < 0.5:
            detected_elements["input_fields"].append((x, y, w, h))
            label = "Input"
        else:
            label = "Element"
        
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    annotated_path = "annotated_ui.png"
    cv2.imwrite(annotated_path, image)
    print("Visual grounding completed. Annotated image saved as", annotated_path)
    print("Detected UI elements:", detected_elements)
    return detected_elements
def execute_command(command: str):
    click_pattern = r"click button at\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)"
    match = re.search(click_pattern, command, re.IGNORECASE)
    if match:
        x, y = int(match.group(1)), int(match.group(2))
        print(f"Simulating click at ({x}, {y})...")
        pyautogui.click(x, y)
    else:
        print("Executing command using tool:", command)
        result = computeruse_tool({"command": command})
        print(result)
def execute_plan(plan: dict):
    if plan.get("screenshot"):
        screenshot_path = capture_screenshot()
        if plan.get("visual_grounding"):
            _ = perform_visual_grounding(screenshot_path)
    command = plan.get("command")
    if command:
        execute_command(command)
    else:
        print("No command found in the plan.")

def main():
    natural_language_task = input("Enter the natural language task: ")
    plan = send_to_llm(natural_language_task)
    print("Structured Plan from LLM:", plan)
    execute_plan(plan)

if __name__ == "__main__":
    main()
