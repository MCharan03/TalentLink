USE sra;
DROP TABLE IF EXISTS user_data;

CREATE TABLE user_data (
    ID INT NOT NULL AUTO_INCREMENT,
    Name VARCHAR(100),
    Email_ID VARCHAR(50),
    -- MODIFIED: Changed to INT for numerical operations
    resume_score INT,
    -- MODIFIED: Changed to DATETIME for proper date handling
    Timestamp DATETIME,
    -- MODIFIED: Changed to INT as it's a number
    Page_no INT,
    Predicted_Field VARCHAR(25),
    User_level VARCHAR(30),
    Actual_skills TEXT,
    Recommended_skills TEXT,
    Recommended_courses TEXT,
    PRIMARY KEY (ID)
);