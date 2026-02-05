from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jieba
from snownlp import SnowNLP

# 初始化Flask应用
app = Flask(__name__)
# 解决跨域问题
CORS(app)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('course.db')
    c = conn.cursor()
    # 创建课程评价表（修正注释符号，使用SQLite支持的--注释）
    c.execute('''
        CREATE TABLE IF NOT EXISTS course_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            comment TEXT NOT NULL,
            score FLOAT,  -- 情感分析得分（0-1，越高越正面）
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 1. 获取所有课程评价
@app.route('/api/comments', methods=['GET'])
def get_comments():
    try:
        conn = sqlite3.connect('course.db')
        conn.row_factory = sqlite3.Row  # 让查询结果可以通过字段名访问
        c = conn.cursor()
        c.execute('SELECT * FROM course_comments ORDER BY create_time DESC')
        comments = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({'code': 200, 'data': comments, 'msg': '查询成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'查询失败：{str(e)}'})

# 2. 提交课程评价并进行情感分析
@app.route('/api/comment', methods=['POST'])
def add_comment():
    try:
        # 获取前端提交的数据
        data = request.get_json()
        course_name = data.get('courseName')
        comment = data.get('comment')
        
        if not course_name or not comment:
            return jsonify({'code': 400, 'msg': '课程名称和评价内容不能为空'})
        
        # 情感分析（SnowNLP的sentiments方法返回0-1的得分）
        s = SnowNLP(comment)
        score = round(s.sentiments, 4)
        
        # 插入数据库
        conn = sqlite3.connect('course.db')
        c = conn.cursor()
        c.execute(
            'INSERT INTO course_comments (course_name, comment, score) VALUES (?, ?, ?)',
            (course_name, comment, score)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'code': 200,
            'data': {'score': score},
            'msg': '评价提交成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'提交失败：{str(e)}'})

# 3. 获取评价统计数据（正面/负面/中性）
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        conn = sqlite3.connect('course.db')
        c = conn.cursor()
        # 统计总数量
        c.execute('SELECT COUNT(*) FROM course_comments')
        total = c.fetchone()[0]
        
        # 统计正面（score>0.6）、负面（score<0.4）、中性（0.4<=score<=0.6）
        c.execute('SELECT COUNT(*) FROM course_comments WHERE score > 0.6')
        positive = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM course_comments WHERE score < 0.4')
        negative = c.fetchone()[0]
        
        neutral = total - positive - negative
        
        conn.close()
        return jsonify({
            'code': 200,
            'data': {
                'total': total,
                'positive': positive,
                'negative': negative,
                'neutral': neutral
            },
            'msg': '统计成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'统计失败：{str(e)}'})

if __name__ == '__main__':
    # 启动后端服务，端口5000，开启调试模式
    app.run(debug=True, host='0.0.0.0', port=5000)