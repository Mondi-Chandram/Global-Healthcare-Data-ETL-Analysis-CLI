-- Table for daily cases
CREATE TABLE IF NOT EXISTS daily_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_date DATE NOT NULL,
    country_name VARCHAR(255) NOT NULL,
    total_cases BIGINT,
    new_cases INT,
    total_deaths BIGINT,
    new_deaths INT,
    etl_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (report_date, country_name)
);

-- Table for vaccination data
CREATE TABLE IF NOT EXISTS vaccination_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_date DATE NOT NULL,
    country_name VARCHAR(255) NOT NULL,
    total_vaccinations BIGINT,
    people_vaccinated BIGINT,
    people_fully_vaccinated BIGINT,
    etl_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (report_date, country_name)
);
