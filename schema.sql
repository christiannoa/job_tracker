-- Job Tracker Database Schema
CREATE DATABASE IF NOT EXISTS job_tracker;
USE job_tracker;

CREATE TABLE IF NOT EXISTS companies (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    website VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT,
    job_title VARCHAR(100) NOT NULL,
    job_type ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min INT,
    salary_max INT,
    job_url VARCHAR(300),
    date_posted DATE,
    requirements JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT,
    application_date DATE NOT NULL,
    status ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn') DEFAULT 'Applied',
    resume_version VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    contact_id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT,
    contact_name VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE SET NULL
);

-- Sample Data
INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp Solutions', 'Technology', 'https://techcorp.com', 'San Francisco', 'CA', 'Fast-growing startup, great culture'),
('DataCo Analytics', 'Data & Analytics', 'https://dataco.io', 'New York', 'NY', 'Remote-friendly, strong data team'),
('CloudBase Inc', 'Cloud Computing', 'https://cloudbase.com', 'Seattle', 'WA', 'Fortune 500 company'),
('StartupXYZ', 'FinTech', 'https://startupxyz.com', 'Austin', 'TX', 'Series B, exciting space');

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, date_posted, requirements) VALUES
(1, 'Software Developer', 'Full-time', 90000, 130000, '2024-01-15', '["Python", "SQL", "Flask", "Docker"]'),
(2, 'Data Analyst', 'Full-time', 75000, 110000, '2024-01-18', '["Python", "SQL", "Tableau", "Excel"]'),
(3, 'Backend Engineer', 'Full-time', 100000, 150000, '2024-01-20', '["Python", "Go", "Kubernetes", "AWS"]'),
(4, 'Full Stack Developer', 'Contract', 80000, 120000, '2024-01-22', '["React", "Node.js", "Python", "MongoDB"]');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2024-01-16', 'Interview', 'v2.1', TRUE, '{"rounds": [{"type": "phone", "date": "2024-01-25", "notes": "Went well"}]}'),
(2, '2024-01-19', 'Screening', 'v2.1', TRUE, NULL),
(3, '2024-01-21', 'Applied', 'v2.0', FALSE, NULL),
(4, '2024-01-23', 'Rejected', 'v2.0', TRUE, NULL);

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Sarah Johnson', 'Engineering Manager', 'sarah@techcorp.com', '415-555-0101', 'https://linkedin.com/in/sarahjohnson', 'Very responsive, met at meetup'),
(2, 'Marcus Chen', 'HR Recruiter', 'marcus@dataco.io', '212-555-0102', 'https://linkedin.com/in/marcuschen', 'Reached out on LinkedIn'),
(3, 'Emily Rodriguez', 'Senior Engineer', 'emily@cloudbase.com', NULL, 'https://linkedin.com/in/emilyrodriguez', 'Employee referral contact');