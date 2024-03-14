CREATE TABLE Sessions (
    SessionID INT NOT NULL AUTO_INCREMENT,
    SessionKey VARCHAR(512),
    DeviceID INT NOT NULL,
    CreationDate VARCHAR(32),
    PRIMARY KEY (SessionID),
    FOREIGN KEY (DeviceID) REFERENCES Devices(DeviceID)
);

CREATE TABLE Users (
    UserID INT NOT NULL AUTO_INCREMENT,
    Forename VARCHAR(32),
    Names VARCHAR(32),
    Email VARCHAR(64),
    PasswordHash VARCHAR(512),
    DateOfBirth CHAR(10),
    PhoneNumber VARCHAR(13),
    Country VARCHAR(16),
    OpenDate CHAR(10),
    PermanentClientPublicKey VARCHAR(256),
    PendingDownload TINYINT,
    NewDeviceCode VARCHAR(6),
    FailedAttemptDate VARCHAR(32) DEFAULT '2000-01-01 00:00:00.000000',
    LoginAttempts TINYINT DEFAULT 0,
    PRIMARY KEY (UserID)
);

CREATE TABLE Passwords (
    PassID INT NOT NULL AUTO_INCREMENT,
    Password VARCHAR(512),
    URL VARCHAR(128),
    Title VARCHAR(32),
    AdditionalInfo VARCHAR(256),
    Username VARCHAR(64),
    Lockdown TINYINT DEFAULT 0,
    PRIMARY KEY (PassID)
);

CREATE TABLE PasswordKeys (
    PassID INT NOT NULL,
    UserID INT NOT NULL,
    PasswordKey VARCHAR(512),
    Manager TINYINT DEFAULT 0,
    PRIMARY KEY (PassID, UserID),
    FOREIGN KEY (PassID) REFERENCES Passwords(PassID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Devices (
    DeviceID INT NOT NULL AUTO_INCREMENT,
    MacAddressHash VARCHAR(512),
    LoginDate VARCHAR(10),
    UserID INT NOT NULL,
    PRIMARY KEY (DeviceID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE PendingPasswords (
    SenderUserID INT NOT NULL,
    RecipientUserID INT NOT NULL,
    PassID INT NOT NULL,
    PasswordKey VARCHAR(512),
    Manager TINYINT DEFAULT 0,
    SymmetricKey VARCHAR(512),
    InsertTime VARCHAR(32),
    PRIMARY KEY (SenderUserID, RecipientUserID, PassID),
    FOREIGN KEY (SenderUserID) REFERENCES Users(UserID),
    FOREIGN KEY (RecipientUserID) REFERENCES Users(UserID),
    FOREIGN KEY (PassID) REFERENCES Passwords(PassID)
);

CREATE TABLE AsymmetricKeys (
    e VARCHAR(256),
    d VARCHAR(256),
    n VARCHAR(256),
    date VARCHAR(32)
);