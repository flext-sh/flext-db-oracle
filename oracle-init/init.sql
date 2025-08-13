-- Oracle Database initialization for FLEXT DB Oracle testing
-- Creates test user and sample schema for functional validation

-- Connect as SYSTEM to create test user
ALTER SESSION SET CONTAINER = XEPDB1;

-- Create test user for FLEXT DB Oracle
CREATE USER flexttest IDENTIFIED BY FlextTest123
  DEFAULT TABLESPACE USERS
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON USERS;

-- Grant necessary privileges
GRANT CONNECT, RESOURCE, CREATE VIEW, CREATE SEQUENCE, CREATE SYNONYM TO flexttest;
GRANT SELECT ANY DICTIONARY TO flexttest;
GRANT CREATE SESSION TO flexttest;

-- NOTE: When running inside docker-compose network, use service hostname
CONNECT flexttest/FlextTest123@//oracle-xe:1521/XEPDB1;

-- Create test tables for functional validation
CREATE TABLE employees (
    employee_id NUMBER(6) PRIMARY KEY,
    first_name VARCHAR2(20),
    last_name VARCHAR2(25) NOT NULL,
    email VARCHAR2(25) NOT NULL UNIQUE,
    phone_number VARCHAR2(20),
    hire_date DATE NOT NULL,
    job_id VARCHAR2(10) NOT NULL,
    salary NUMBER(8,2),
    commission_pct NUMBER(2,2),
    manager_id NUMBER(6),
    department_id NUMBER(4),
    created_date DATE DEFAULT SYSDATE,
    CONSTRAINT emp_salary_min CHECK (salary > 0)
);

CREATE TABLE departments (
    department_id NUMBER(4) PRIMARY KEY,
    department_name VARCHAR2(30) NOT NULL,
    manager_id NUMBER(6),
    location_id NUMBER(4),
    created_date DATE DEFAULT SYSDATE
);

CREATE TABLE jobs (
    job_id VARCHAR2(10) PRIMARY KEY,
    job_title VARCHAR2(35) NOT NULL,
    min_salary NUMBER(6),
    max_salary NUMBER(6),
    created_date DATE DEFAULT SYSDATE
);

-- Create sequences
CREATE SEQUENCE emp_seq START WITH 1000 INCREMENT BY 1;
CREATE SEQUENCE dept_seq START WITH 100 INCREMENT BY 10;

-- Create indexes
CREATE INDEX emp_name_idx ON employees(last_name, first_name);
CREATE INDEX emp_dept_idx ON employees(department_id);

-- Create view
CREATE VIEW emp_details_view AS
SELECT 
    e.employee_id,
    e.first_name || ' ' || e.last_name AS full_name,
    e.email,
    e.salary,
    d.department_name,
    j.job_title
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN jobs j ON e.job_id = j.job_id;

-- Insert test data
INSERT INTO departments VALUES (10, 'Administration', NULL, 1700, SYSDATE);
INSERT INTO departments VALUES (20, 'Marketing', NULL, 1800, SYSDATE);
INSERT INTO departments VALUES (30, 'Purchasing', NULL, 1700, SYSDATE);
INSERT INTO departments VALUES (40, 'Human Resources', NULL, 2400, SYSDATE);
INSERT INTO departments VALUES (50, 'Shipping', NULL, 1500, SYSDATE);

INSERT INTO jobs VALUES ('AD_PRES', 'President', 20000, 40000, SYSDATE);
INSERT INTO jobs VALUES ('AD_VP', 'Administration Vice President', 15000, 30000, SYSDATE);
INSERT INTO jobs VALUES ('AD_ASST', 'Administration Assistant', 3000, 6000, SYSDATE);
INSERT INTO jobs VALUES ('IT_PROG', 'Programmer', 4000, 10000, SYSDATE);
INSERT INTO jobs VALUES ('ST_CLERK', 'Stock Clerk', 2000, 5000, SYSDATE);

INSERT INTO employees VALUES (1001, 'Steven', 'King', 'SKING', '515.123.4567', DATE '2003-06-17', 'AD_PRES', 24000, NULL, NULL, 10, SYSDATE);
INSERT INTO employees VALUES (1002, 'Neena', 'Kochhar', 'NKOCHHAR', '515.123.4568', DATE '2005-09-21', 'AD_VP', 17000, NULL, 1001, 10, SYSDATE);
INSERT INTO employees VALUES (1003, 'Lex', 'De Haan', 'LDEHAAN', '515.123.4569', DATE '2001-01-13', 'AD_VP', 17000, NULL, 1001, 10, SYSDATE);
INSERT INTO employees VALUES (1004, 'Alexander', 'Hunold', 'AHUNOLD', '590.423.4567', DATE '2006-01-03', 'IT_PROG', 9000, NULL, 1003, 20, SYSDATE);
INSERT INTO employees VALUES (1005, 'Bruce', 'Ernst', 'BERNST', '590.423.4568', DATE '2007-05-21', 'IT_PROG', 6000, NULL, 1004, 20, SYSDATE);

-- Commit changes
COMMIT;

-- Display summary
SELECT 'Tables created: ' || COUNT(*) AS result FROM user_tables;
SELECT 'Sequences created: ' || COUNT(*) AS result FROM user_sequences;
SELECT 'Views created: ' || COUNT(*) AS result FROM user_views;
SELECT 'Employees inserted: ' || COUNT(*) AS result FROM employees;
SELECT 'Departments inserted: ' || COUNT(*) AS result FROM departments;

EXIT;