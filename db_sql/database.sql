create database strategy;
create user strategy_user with login encrypted password 'strategy_pass';
grant all privileges on database strategy to strategy_user;

CREATE TABLE trades (
	"Number" integer, 
	"Trade type" character varying(50),
	"Entry time" character varying(50),
	"Exposure"  character varying(100),
	"Entry balance" float(6),
	"Exit balance" float(6),
	"Profit" float(6),
	"Pnl (incl fees)" float(6),
	"Exchange"  character varying(50), 
	"Margin" integer,
	"BTC Price" float(6)
	);

