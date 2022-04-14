DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS measurement;
DROP TABLE IF EXISTS totmode;
DROP TABLE IF EXISTS totmode_hist;
DROP TABLE IF EXISTS dosimode;
DROP TABLE IF EXISTS integrationmode;
DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS thl_calib;
DROP TABLE IF EXISTS thl_calib_data;
DROP TABLE IF EXISTS equal;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE measurement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    config_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    mode TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (config_id) REFERENCES config (id),
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE totmode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL,
    frame_id INTEGER NOT NULL,
    value INTEGER NOT NULL,
    FOREIGN KEY (measurement_id) REFERENCES measurement (id)
);

CREATE TABLE totmode_hist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL,
    pixel_id INTEGER NOT NULL,
    bin INTEGER NOT NULL,
    value INTEGER NOT NULL,
    FOREIGN KEY (measurement_id) REFERENCES measurement (id)
);

CREATE TABLE dosimode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL,
    frame_id INTEGER NOT NULL,
    bin0 INTEGER NOT NULL,
    bin1 INTEGER NOT NULL,
    bin2 INTEGER NOT NULL,
    bin3 INTEGER NOT NULL,
    bin4 INTEGER NOT NULL,
    bin5 INTEGER NOT NULL,
    bin6 INTEGER NOT NULL,
    bin7 INTEGER NOT NULL,
    bin8 INTEGER NOT NULL,
    bin9 INTEGER NOT NULL,
    bin10 INTEGER NOT NULL,
    bin11 INTEGER NOT NULL,
    bin12 INTEGER NOT NULL,
    bin13 INTEGER NOT NULL,
    bin14 INTEGER NOT NULL,
    bin15 INTEGER NOT NULL,
    FOREIGN KEY (measurement_id) REFERENCES measurement (id)
);

CREATE TABLE integrationmode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL,
    frame_id INTEGER NOT NULL,
    pixel_id INTEGER NOT NULL,
    value INTEGER NOT NULL,
    FOREIGN KEY (measurement_id) REFERENCES measurement (id)
);

CREATE TABLE config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    dosepix_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    i_krum INTEGER NOT NULL DEFAULT 50,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    v_casc_preamp INTEGER DEFAULT 130,
    v_casc_reset INTEGER DEFAULT 220,
    i_pixeldac INTEGER DEFAULT 49,
    i_tpbufin INTEGER DEFAULT 128,
    v_tpref_fine INTEGER DEFAULT 100,
    v_gnd INTEGER DEFAULT 80,
    i_disc2 INTEGER DEFAULT 118,
    i_disc1 INTEGER DEFAULT 48,
    i_preamp INTEGER DEFAULT 100,
    v_tpref_coarse INTEGER DEFAULT 255,
    i_tpbufout INTEGER DEFAULT 128,
    v_fbk INTEGER DEFAULT 200,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE thl_calib (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    config_id INTEGER NOT NULL,
    FOREIGN KEY (config_id) REFERENCES config (id)
);

CREATE TABLE thl_calib_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thl_calib_id INTEGER NOT NULL,
    volt REAL NOT NULL,
    ADC INTEGER NOT NULL,
    FOREIGN KEY (thl_calib_id) REFERENCES thl_calib (id)
);

CREATE TABLE equal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    v_tha INTEGER DEFAULT 5271,
    confbits TEXT DEFAULT '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
    pixeldac TEXT DEFAULT '00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
    FOREIGN KEY (config_id) REFERENCES config (id)
);
