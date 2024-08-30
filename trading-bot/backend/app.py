# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, TradingStrategy, TradeData
from trading_bot import TradingBot

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading_bot.db'
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this!
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = User(username=data['username'], password=bcrypt.generate_password_hash(data['password']))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/strategy', methods=['POST'])
@jwt_required()
def create_strategy():
    data = request.json
    strategy = TradingStrategy(name=data['name'], code=data['code'], language=data['language'])
    db.session.add(strategy)
    db.session.commit()
    return jsonify({"message": "Strategy created successfully"}), 201

@app.route('/start_trading', methods=['POST'])
@jwt_required()
def start_trading():
    data = request.json
    user_id = get_jwt_identity()
    bot = TradingBot(data['api_key'], data['api_secret'], data['symbol'], data['timeframe'], 
                     data['strategy_id'], data['initial_balance'], data['mode'])
    # Start the bot in a separate thread
    bot.start()
    return jsonify({"message": "Trading started"}), 200

@app.route('/stop_trading', methods=['POST'])
@jwt_required()
def stop_trading():
    # Implement logic to stop the trading bot
    return jsonify({"message": "Trading stopped"}), 200

@app.route('/trade_data', methods=['GET'])
@jwt_required()
def get_trade_data():
    # Implement logic to retrieve trade data for analysis
    trade_data = TradeData.query.all()
    return jsonify([data.to_dict() for data in trade_data]), 200

if __name__ == '__main__':
    app.run(debug=True)

