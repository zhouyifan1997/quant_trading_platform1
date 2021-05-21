STOCK_BASIC_INFO_QUERY = """
SELECT * FROM stock_basic_info WHERE stock_code = "%s" and stock_info_date = "%s"
"""
EMA_INFO_QUERY = """
SELECT * FROM ema_info WHERE stock_code = "%s" and ema_info_date = "%s"
"""
STOCK_QUERY = """
SELECT * FROM stock;
"""
USER_QUERY = """
SELECT * FROM user WHERE email = '%s';
"""
USER_WATCH_QUERY = """
SELECT stock_code FROM user_watch_list WHERE user_id = %d;
"""
USER_BUY_QUERY = """
SELECT stock_code FROM user_buy_list WHERE user_id = %d;
"""
VERIFICATION_STOCK_QUERY = """
SELECT * FROM verification_stock_list;
"""
RECOMMENDATION_STOCK_QUERY = """
SELECT * FROM recommendation_stock_list;
"""
WEEKDAY_QUERY = """
SELECT * FROM stock_basic_info where stock_info_date = "%s" and stock_code = "AAPL";
"""
INSERT_VERIFICATION_STOCK_QUERY = """
INSERT INTO verification_stock_list (stock_code) VALUES ('%s');
"""
INSERT_WATCHLIST_STOCK_QUERY = """
INSERT INTO watch_stock_list (stock_code) VALUES ('%s');
"""
INSERT_RECOMMENDATION_STOCK_QUERY = """
INSERT INTO recommendation_stock_list (stock_code) VALUES ('%s');
"""
INSERT_STOCK_QUERY = """
INSERT INTO stock (code) VALUES ('%s');
"""
INSERT_STOCK_BASIC_INFO_QUERY = """
INSERT INTO stock_basic_info (stock_code, stock_info_date, open, close, high, low, volume)
VALUES 
"""
INSERT_EMA_INFO_QUERY = """
INSERT INTO ema_info (stock_code, ema_info_date, one, two, three, four, five)
VALUES
"""
INSERT_USER_QUERY = """
INSERT INTO user (email, username, password, first_name, last_name)
VALUES
('%s', '%s', '%s', '%s', '%s');
"""
INSERT_USER_WATCH_QUERY = """
INSERT INTO user_watch_list (user_id, stock_code)
VALUES
(%d, '%s');
"""
INSERT_USER_BUY_QUERY = """
INSERT INTO user_buy_list (user_id, stock_code)
VALUES
(%d, '%s');
"""
DATA_FORMAT = """('%s', '%s', %.4f, %.4f, %.4f, %.4f, %.4f),"""

DELETE_USER_WATCH_QUERY = """
DELETE FROM user_watch_list
WHERE
user_id = %d and stock_code = '%s';
"""
DELETE_USER_BUY_QUERY = """
DELETE FROM user_buy_list
WHERE
user_id = %d and stock_code = '%s';
"""
DESTROY_DATABASE_QUERY = [
"DROP TABLE IF EXISTS stock_ema_info;",
"DROP TABLE IF EXISTS stock_basic_info;",
"DROP TABLE IF EXISTS recommendation_stock_list;",
"DROP TABLE IF EXISTS user;",
"DROP TABLE IF EXISTS user_buy_list;",
"DROP TABLE IF EXISTS user_watch_list;",
"DROP TABLE IF EXISTS stock;",
]
INIT_DATABASE_QUERY = [
"""
CREATE TABLE stock (
	stock_code VARCHAR(255) NOT NULL,
    PRIMARY KEY (stock_code)
);
""",
"""
CREATE TABLE stock_basic_info (
	stock_basic_info_id INT NOT NULL AUTO_INCREMENT,
	stock_code VARCHAR(255) NOT NULL,
	stock_info_date DATE NOT NULL,
	open FLOAT NOT NULL,
	close float NOT NULL,
	high float NOT NULL,
	low float NOT NULL,
	volume BigInt NOT NULL,
    PRIMARY KEY(stock_basic_info_id),
    FOREIGN KEY (stock_code) REFERENCES stock(stock_code),
	UNIQUE(stock_code, stock_info_date)
);
""",
"""
CREATE TABLE stock_ema_info (
	stock_ema_info_id INT NOT NULL AUTO_INCREMENT,
	stock_code VARCHAR(255) NOT NULL,
	stock_info_date DATE NOT NULL,
	one FLOAT NOT NULL,
	two FLOAT NOT NULL,
	three FLOAT NOT NULL,
	four FLOAT NOT NULL,
	five FLOAT,
	PRIMARY KEY(stock_ema_info_id),
    FOREIGN KEY (stock_code) REFERENCES stock(stock_code),
	UNIQUE(stock_code, stock_info_date)
);
""",
"""
CREATE TABLE recommendation_stock_list (
	stock_code VARCHAR(255) NOT NULL,
	PRIMARY KEY(stock_code)
);
""",
"""
CREATE TABLE user (
	user_id INT NOT NULL AUTO_INCREMENT,
	email VARCHAR(255) NOT NULL,
	username VARCHAR(255) NOT NULL,
	password VARCHAR(255) NOT NULL,
	first_name VARCHAR(255),
	last_name VARCHAR(255),
	PRIMARY KEY(user_id),
	UNIQUE(email, username)
);
""",
"""
CREATE TABLE user_watch_list (
	user_id INT NOT NULL,
	stock_code VARCHAR(255) NOT NULL,
	PRIMARY KEY(user_id, stock_code)
);
""",
"""
CREATE TABLE user_buy_list (
	user_id INT NOT NULL,
	stock_code VARCHAR(255) NOT NULL,
	PRIMARY KEY(user_id, stock_code)
);
"""
]
LAST_UPDATE_BASIC_INFO_DATE_QUERY = """
SELECT stock_info_date FROM stock_basic_info
WHERE
stock_code = '%s'
ORDER BY stock_info_date DESC
LIMIT 1;
"""
LAST_UPDATE_EMA_INFO_DATE_QUERY = """
SELECT ema_info_date FROM ema_info
WHERE
stock_code = '%s'
ORDER BY ema_info_date DESC
LIMIT 1;
"""