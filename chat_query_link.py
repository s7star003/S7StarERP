from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/go_chat_query')
def go_chat_query():
    # 这里可以自定义问题
    question = request.args.get('q', '请统计每个商品的销量')
    # POST到Django chatQuery接口
    resp = requests.post('http://localhost:8000/api/TikTok/chatQuery', json={"question": question})
    return jsonify(resp.json())

if __name__ == '__main__':
    app.run(port=5003, debug=True) 