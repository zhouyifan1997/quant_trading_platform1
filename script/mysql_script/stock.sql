CREATE TABLE stock (
	code VARCHAR(255) NOT NULL,
    PRIMARY KEY (code)
);

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
    FOREIGN KEY (stock_code) REFERENCES stock(code),
	UNIQUE(stock_code, stock_info_date)
);


CREATE TABLE ema_info (
	ema_info_id INT NOT NULL AUTO_INCREMENT,
	stock_code VARCHAR(255) NOT NULL,
	ema_info_date DATE NOT NULL,
	one FLOAT NOT NULL,
	two FLOAT NOT NULL,
	three FLOAT NOT NULL,
	four FLOAT NOT NULL,
	five FLOAT,
	PRIMARY KEY(ema_info_id),
    FOREIGN KEY (stock_code) REFERENCES stock(code),
	UNIQUE(stock_code, ema_info_date)
);

CREATE TABLE watch_stock_list (
	stock_code VARCHAR(255) NOT NULL,
	PRIMARY KEY(stock_code)
);

CREATE TABLE verification_stock_list (
	stock_code VARCHAR(255) NOT NULL,
	PRIMARY KEY(stock_code)
);

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

CREATE TABLE user_watch_list (
	user_id INT NOT NULL,
	stock_code VARCHAR(255) NOT NULL,
	PRIMARY KEY(user_id, stock_code)
);

CREATE TABLE user_buy_list (
	user_id INT NOT NULL,
	stock_code VARCHAR(255) NOT NULL,
	PRIMARY KEY(user_id, stock_code)
);