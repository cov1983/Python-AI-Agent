"""
A simple command-line interface to interact with the Gemini API and execute functions based on model responses.
This version of the code has been refactored to improve readability and maintainability by breaking down the main function into smaller, more focused functions. 
Each function has a single responsibility, making it easier to understand and modify individual parts of the code without affecting the overall structure. 
Additionally, error handling has been added to ensure that any issues with the API response or function calls are properly caught and reported.
"""

import os
import argparse

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from config import GEMINI_MODEL, MAX_ITERATIONS
from call_function import available_functions, call_function


def parse_args():
    parser = argparse.ArgumentParser(
        description="A simple command-line interface to interact with the Gemini API and execute functions based on model responses."
    )
    parser.add_argument("user_prompt", type=str, help="The prompt to send to the Gemini API")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def create_client():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment variables")
    return genai.Client(api_key=api_key)


def build_initial_messages(user_prompt):
    return [types.Content(role="user", parts=[types.Part(text=user_prompt)])]


def append_candidate_messages(messages, response):
    if not response.candidates:
        return False

    for candidate in response.candidates:
        messages.append(candidate.content)
    return True


def validate_function_call_response(function_call_response):
    if not function_call_response.parts:
        raise RuntimeError("Function call response appears to be malformed: missing parts")
    if function_call_response.parts[0].function_response is None:
        raise RuntimeError("Function call response appears to be malformed: missing function_response")
    if function_call_response.parts[0].function_response.response is None:
        raise RuntimeError("Function call response appears to be malformed: missing function_response.response")


def execute_function_calls(response, verbose):
    function_results = []

    for function_call in response.function_calls:
        function_call_response = call_function(function_call, verbose=verbose)
        validate_function_call_response(function_call_response)
        function_results.append(function_call_response)

    return function_results


def print_verbose_output(args, response, function_results):
    print(f"User prompt: {args.user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    print(f"Response: \n{function_results}")


def generate_content(client, model, args, messages):
    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
        ),
    )

    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed: missing usage_metadata")

    if not response.function_calls:
        print("No more function calls, final response:")
        print(response.text)
        return response, []

    function_results = execute_function_calls(response, args.verbose)

    if args.verbose:
        print_verbose_output(args, response, function_results)

    return response, function_results


def run_agent_loop(client, model, args, messages):
    for iteration in range(MAX_ITERATIONS):
        response, function_results = generate_content(client, model, args, messages)

        if not append_candidate_messages(messages, response):
            print("No candidates in response, ending loop.")
            break

        if function_results:
            messages.extend(function_results)

        if not response.function_calls:
            print("No more function calls, ending loop.")
            break

        if iteration == MAX_ITERATIONS - 1:
            print("Maximum iterations reached, ending loop.")
            exit(1)


def main():
    args = parse_args()
    client = create_client()
    messages = build_initial_messages(args.user_prompt)
    run_agent_loop(client, GEMINI_MODEL, args, messages)


if __name__ == "__main__":
    main()