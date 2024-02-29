from flask import Flask, request, render_template,jsonify
from openai import OpenAI
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*', supports_credentials=True) 
openai_key = OpenAI(
    api_key='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'
)

# @app.route('/')
# def home():
#     return render_template('index.html', data = None, similar_prompts = None)

# Function to generate response with suggestions
@app.route('/generate-response', methods=['POST'])
def generate_response():
    if request.method == 'POST':
        request_data = request.get_json()
        user_prompt = request_data['prompt']
        print(user_prompt)
        
        
        system_message_content="You have to create a response for this user prompt. Also using your capabilities you should understand the prompt and create response in the format necesarry like normal text, markdown, list, bullet points. for next line add \\n in the response where new line starts."
        messages = [
                {
                    "role": "system",
                    "content": system_message_content
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        response = openai_key.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            max_tokens=4096,
            temperature=0.7
        )

        suggested_prompt=[]
        suggested_prompts_system_content = """
            Given a user prompt about a general interest or query, generate a list of 3 to 5 suggested prompts that are related to the original prompt but offer different perspectives, detailed inquiries, or specific focuses. The suggested prompts should explore various aspects of the topic, providing users with options to narrow down or expand their search in related areas. Ensure that the suggestions are diverse and cover a range of interests that might be relevant to the original query. Format the output as a numbered list, with each suggestion on a new line, preceded by its number followed by a period and a space. Use the format:

            1. Suggested prompt 1\\n
            2. Suggested prompt 2\\n
            3. Suggested prompt 3\\n
            ...
            Ensure that each suggestion is concise and directly related to the original query, offering a clear direction for further exploration or specificity.
            """
        messages = [
                {
                    "role": "system",
                    "content": suggested_prompts_system_content
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        suggested_prompts_response = openai_key.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        response_content = response.choices[0].message.content.strip().replace("**", "")
        response_text_content = suggested_prompts_response.choices[0].message.content.strip()
        response_content_suggested = [line.strip() for line in response_text_content.split('\n') if line]
        formatted_suggestions_list = [suggestion.split('. ', 1)[-1].strip() if '. ' in suggestion else suggestion.strip() for suggestion in response_content_suggested]
        suggested_prompt.append(formatted_suggestions_list)
        print(suggested_prompt)
        # print(parsed_data_suggested)
        
        print(response_content)
        

        return jsonify({
            "response": response_content,
            "similar_prompts": suggested_prompt
        })
    else:
        return jsonify({"response": None, "similar_prompts": None})

if __name__ == "__main__":
    app.run(debug=True)
