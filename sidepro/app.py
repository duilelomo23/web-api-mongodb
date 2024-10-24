import pymongo
from flask import *
import bcrypt
from flask_mail import Mail, Message
import os
import secrets



client = pymongo.MongoClient('mongodb+srv://root:ji394su3@mycluster.pvixzf4.mongodb.net/?retryWrites=true&w=majority&appName=MyCluster')
db = client.member_system

print('資料庫建立成功')

app = Flask(
    __name__,
    static_folder='public',
    static_url_path='/'
)

app.secret_key = 'ant string but secret'




#處理路由
@app.route("/")
def index():
    return render_template('index.html')

#會員頁面
@app.route('/member') 
def member():
    if 'nickname' in session:
        user_email = session['email']
        collection = db.user
        user = collection.find_one({'email': user_email})
        print(user)
        
        # 获取好友列表
        friends = user.get('friends', [])
        
        return render_template('member.html', 
                               message=session['nickname'], 
                               friends=friends)
    else:
        return redirect('/signin')

#註冊會員頁面
@app.route('/new_member')
def new_member():
    return render_template('new_member.html')
    

@app.route('/error')
def error():
    message = request.args.get('msg', '發生錯誤請重新嘗試')
    return render_template('error.html', message=message)


#註冊
@app.route('/signup', methods=['POST'])
def signup():
    #從前端藉收資料
    nickname = request.form['nickname']
    email = request.form['email']
    #密碼轉字節 做哈希處理
    password = request.form['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    print(hashed_password)
    #根據收到的資料 跟資料庫互動
    collection = db.user
    print(collection)
    
    #檢查集合是否有相同 email 資料
    result = collection.find_one({
        'email':email
    })
    if result != None:
        return redirect('/error?msg=信箱以註冊')
    #mickname email paasword 新增到資料庫 
    collection.insert_one({
        'nickname':nickname,
        'email':email,
        'password':hashed_password
    })
    return redirect('/')


#登入檢查
@app.route('/signin', methods=['POST'])
def signin():
    #從前端取的使用者輸入資料
    email=request.form['email']
    password = request.form['password']
    #和資料庫互動
    session['email'] = email
    collection = db.user

    #取的資料庫對應信箱的所有資料  id name email password
    result = collection.find_one({'email': email})
   
    
    #先檢查帳號後檢查密碼
    if result is None:
        return redirect('/error?msg=輸入信箱錯誤')
    else:
        #哈希解密
        
        #登入成功 在 session 紀錄會員資訊 導向到會員頁面
        if bcrypt.checkpw(password.encode('utf-8'), result['password']):
            session['nickname'] = result['nickname']
            return redirect('/member')
        else:
            return redirect('/error?msg=輸入密碼錯誤')
    
#登出
@app.route('/signout')
def signout():
    del session['nickname']
    return redirect('/')


@app.route('/add_html')
def add_html():
    return render_template('add_friend.html')



#修改名稱或密碼畫面
@app.route('/updata_html', methods=['POST'])
def updata_html():
    return render_template('updata_profile.html')



#更新名稱
@app.route('/updata_name', methods=['POST'])
def updata_name():
    if 'nickname' in session:
        new_nickname = request.form.get('new_nickname')    #get 使用 request.args.get()   post 使用 request.form.get()
        #判斷輸入名稱是否為空
        if not new_nickname or not new_nickname.strip():
            return redirect('/error?msg=未填寫名稱')

        collection = db.user
        print('你輸入的名稱:', new_nickname)
        if new_nickname != session['nickname']:
            #使用信箱尋找資料庫檔案而不是使用nickname會倒置nickname重複修改到其他資料
            collection.update_one(
                {'email': session['email']},
                {'$set': {'nickname': new_nickname}}              #$set 更新資料庫
            )
            # 更新 session 中的昵称
            session['nickname'] = new_nickname
            return redirect('/error?msg=名稱已更新')
        else:
            return redirect('/error?msg=輸入不同的名稱')
    return redirect('/member')
    

#更新密碼api
@app.route('/updata_password', methods=['POST'])
def updata_password():
    if 'nickname' in session:
        # 从前端获取的数据
        email = request.form.get('email')
        password = request.form.get('password').encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        collection = db.user

        if email is not None:
            email_exists = collection.find_one({'email': email})

            if email_exists is not None:
                collection.update_one(
                    {'email': email},
                    {'$set': {'password': hashed_password}}
                )
                return redirect('/')
                
            else:
                return redirect('/error?msg=信箱輸入錯誤')
        else:
            return redirect('/error?msg=請輸入密碼')

    return redirect('/')

    

if __name__ == '__main__':
    app.run(port=3000, debug=True)


                           