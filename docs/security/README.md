# Oracle Database Security Guide

Comprehensive guide covering all aspects of Oracle Database security, from basic authentication to advanced security features.

## ü"ã Table of Contents

- [Security Overview](#security-overview)
- [Authentication](#authentication)
- [Authorization](#authorization)
- [Data Encryption](#data-encryption)
- [Network Security](#network-security)
- [Auditing](#auditing)
- [Advanced Security Features](#advanced-security-features)
- [Security Compliance](#security-compliance)
- [Security Best Practices](#security-best-practices)
- [Security Monitoring](#security-monitoring)

## üõ°Ô∏è Security Overview

### Oracle Database Security Architecture

```
‚"å‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ê
‚"Ç                Oracle Database Security Layers              ‚"Ç
‚"ú‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"§
‚"Ç Application Security                                        ‚"Ç
‚"Ç ‚"å‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ê ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Application-level authentication                      ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Data validation and sanitization                     ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚"Ç ‚Ä¢ Session management                                  ‚"Ç ‚"Ç
‚"Ç ‚""‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ò ‚"Ç
‚"ú‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"§
‚"Ç Database Security                                           ‚"Ç
‚"Ç ‚"å‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ê ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ User authentication and authorization                 ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Role-based access control                            ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Virtual Private Database (VPD)                       ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚"Ç ‚Ä¢ Database Vault                                      ‚"Ç ‚"Ç
‚"Ç ‚""‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ò ‚"Ç
‚"ú‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"§
‚"Ç Data Security                                               ‚"Ç
‚"Ç ‚"å‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ê ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Transparent Data Encryption (TDE)                    ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Data Redaction                                       ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Oracle Label Security                                ‚"Ç ‚"Ç
‚"Ç ‚""‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ò ‚"Ç
‚"ú‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"§
‚"Ç Network Security                                            ‚"Ç
‚"Ç ‚"å‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ê ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Oracle Net encryption                                 ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ SSL/TLS connections                                   ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ Connection filtering                                  ‚"Ç ‚"Ç
‚"Ç ‚""‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ò ‚"Ç
‚"ú‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"§
‚"Ç Operating System Security                                   ‚"Ç
‚"Ç ‚"å‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ê ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ OS user authentication                                ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ File system permissions                               ‚"Ç ‚"Ç
‚"Ç ‚"Ç ‚Ä¢ OS auditing                                          ‚"Ç ‚"Ç
‚"Ç ‚""‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ò ‚"Ç
‚""‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"Ä‚"ò
```

### Security Principles

#### Defense in Depth

- **Multiple Security Layers**: Implement security at all levels
- **Redundant Controls**: Backup security mechanisms
- **Fail-Safe Defaults**: Secure by default configuration

#### Least Privilege

- **Minimum Required Access**: Grant only necessary privileges
- **Role-Based Access**: Use roles instead of direct grants
- **Regular Reviews**: Periodic access reviews

#### Separation of Duties

- **Administrative Separation**: Separate DBA and security roles
- **Development vs. Production**: Different access levels
- **Audit Independence**: Independent audit functions

## ü"ê Authentication

### Database Authentication

#### Password Authentication

```sql
-- Create user with password
CREATE USER john_doe IDENTIFIED BY "SecurePassword123!";

-- Password complexity verification
ALTER PROFILE DEFAULT LIMIT
    PASSWORD_VERIFY_FUNCTION ora12c_verify_function
    PASSWORD_LIFE_TIME 90
    PASSWORD_GRACE_TIME 7
    PASSWORD_REUSE_TIME 365
    PASSWORD_REUSE_MAX 5
    FAILED_LOGIN_ATTEMPTS 3
    PASSWORD_LOCK_TIME 1;

-- Custom password verification function
CREATE OR REPLACE FUNCTION custom_verify_function(
    username VARCHAR2,
    password VARCHAR2,
    old_password VARCHAR2
) RETURN BOOLEAN IS
BEGIN
    -- Check minimum length
    IF LENGTH(password) < 12 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Password must be at least 12 characters');
    END IF;

    -- Check complexity requirements
    IF NOT REGEXP_LIKE(password, '[A-Z]') THEN
        RAISE_APPLICATION_ERROR(-20002, 'Password must contain uppercase letter');
    END IF;

    IF NOT REGEXP_LIKE(password, '[a-z]') THEN
        RAISE_APPLICATION_ERROR(-20003, 'Password must contain lowercase letter');
    END IF;

    IF NOT REGEXP_LIKE(password, '[0-9]') THEN
        RAISE_APPLICATION_ERROR(-20004, 'Password must contain number');
    END IF;

    IF NOT REGEXP_LIKE(password, '[!@#$%^&*()_+=-]') THEN
        RAISE_APPLICATION_ERROR(-20005, 'Password must contain special character');
    END IF;

    RETURN TRUE;
END;
/
```

#### External Authentication

##### Operating System Authentication

```sql
-- Create OS authenticated user
CREATE USER ops$oracle IDENTIFIED EXTERNALLY;
GRANT CONNECT TO ops$oracle;

-- Configure OS authentication
ALTER SYSTEM SET os_authent_prefix = 'ops$';
ALTER SYSTEM SET remote_os_authent = FALSE;
```

##### LDAP Authentication

```sql
-- Configure LDAP authentication
ALTER SYSTEM SET ldap_directory_access = PASSWORD;

-- Create LDAP authenticated user
CREATE USER "cn=john.doe,ou=people,dc=company,dc=com"
IDENTIFIED GLOBALLY AS 'CN=John Doe,OU=People,DC=company,DC=com';
```

##### Kerberos Authentication

```sql
-- Configure Kerberos
ALTER SYSTEM SET kerberos_realm = 'COMPANY.COM';
ALTER SYSTEM SET kerberos_keytab = '/etc/krb5.keytab';

-- Create Kerberos user
CREATE USER john_doe IDENTIFIED EXTERNALLY AS 'john.doe@COMPANY.COM';
```

### Strong Authentication

#### Multi-Factor Authentication

```sql
-- Enable strong authentication
ALTER SYSTEM SET sec_case_sensitive_logon = TRUE;
ALTER SYSTEM SET sec_max_failed_login_attempts = 3;
ALTER SYSTEM SET sec_protocol_error_further_action = DROP;
```

#### Certificate-Based Authentication

```sql
-- Configure SSL authentication
ALTER SYSTEM SET ssl_client_authentication = TRUE;

-- Create certificate-mapped user
CREATE USER john_doe IDENTIFIED EXTERNALLY AS
'CN=John Doe,OU=IT,O=Company,C=US';
```

### Privileged User Authentication

#### SYSDBA/SYSOPER Authentication

```sql
-- Password file authentication
orapwd file=$ORACLE_HOME/dbs/orapwORCL password=SysPassword entries=10

-- Grant SYSDBA privilege
GRANT SYSDBA TO john_doe;

-- Connect as SYSDBA
CONNECT john_doe/password AS SYSDBA;
```

#### Common User Authentication (Multitenant)

```sql
-- Create common user
CREATE USER c##dba_user IDENTIFIED BY "SecurePassword123!"
CONTAINER = ALL;

-- Grant privileges in all containers
GRANT SYSDBA TO c##dba_user CONTAINER = ALL;
```

## ü"ë Authorization

### Privilege Management

#### System Privileges

```sql
-- Grant system privileges
GRANT CREATE SESSION TO john_doe;
GRANT CREATE TABLE TO john_doe;
GRANT CREATE PROCEDURE TO john_doe;
GRANT UNLIMITED TABLESPACE TO john_doe;

-- Revoke system privileges
REVOKE UNLIMITED TABLESPACE FROM john_doe;

-- Query system privileges
SELECT grantee, privilege, REDACTED_LDAP_BIND_PASSWORD_option
FROM dba_sys_privs
WHERE grantee = 'JOHN_DOE';
```

#### Object Privileges

```sql
-- Grant object privileges
GRANT SELECT, INSERT, UPDATE ON employees TO john_doe;
GRANT EXECUTE ON hr_package TO john_doe;

-- Grant with grant option
GRANT SELECT ON employees TO john_doe WITH GRANT OPTION;

-- Column-level privileges
GRANT UPDATE (salary, commission) ON employees TO john_doe;

-- Revoke object privileges
REVOKE INSERT, UPDATE ON employees FROM john_doe;

-- Query object privileges
SELECT owner, table_name, privilege, grantable
FROM dba_tab_privs
WHERE grantee = 'JOHN_DOE';
```

### Role-Based Access Control

#### Creating and Managing Roles

```sql
-- Create role
CREATE ROLE hr_manager;
CREATE ROLE hr_employee;

-- Grant privileges to role
GRANT CREATE SESSION TO hr_employee;
GRANT SELECT ON hr.employees TO hr_employee;
GRANT SELECT, INSERT, UPDATE ON hr.employees TO hr_manager;

-- Grant role to user
GRANT hr_employee TO john_doe;
GRANT hr_manager TO jane_smith;

-- Create secure role with password
CREATE ROLE sensitive_data_access IDENTIFIED BY "RolePassword123!";

-- Enable/disable roles
ALTER USER john_doe DEFAULT ROLE hr_employee;
SET ROLE hr_manager IDENTIFIED BY "RolePassword123!";
```

#### Role Hierarchies

```sql
-- Create role hierarchy
CREATE ROLE junior_analyst;
CREATE ROLE senior_analyst;
CREATE ROLE data_manager;

-- Grant basic privileges to junior role
GRANT CREATE SESSION TO junior_analyst;
GRANT SELECT ON reporting.sales_data TO junior_analyst;

-- Grant junior role to senior role
GRANT junior_analyst TO senior_analyst;
GRANT INSERT, UPDATE ON reporting.sales_data TO senior_analyst;

-- Grant senior role to manager role
GRANT senior_analyst TO data_manager;
GRANT DELETE ON reporting.sales_data TO data_manager;
```

### Virtual Private Database (VPD)

#### Row-Level Security

```sql
-- Create security policy function
CREATE OR REPLACE FUNCTION employee_security_policy(
    schema_var IN VARCHAR2,
    table_var IN VARCHAR2
) RETURN VARCHAR2 IS
    predicate VARCHAR2(400);
BEGIN
    -- Managers can see all employees in their department
    IF SYS_CONTEXT('USERENV', 'SESSION_USER') = 'MANAGER' THEN
        predicate := 'department_id = SYS_CONTEXT(''USER_CTX'', ''DEPT_ID'')';
    -- Employees can only see their own record
    ELSE
        predicate := 'employee_id = SYS_CONTEXT(''USERENV'', ''CLIENT_IDENTIFIER'')';
    END IF;

    RETURN predicate;
END;
/

-- Create security policy
BEGIN
    DBMS_RLS.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        policy_name => 'EMPLOYEE_SECURITY_POLICY',
        function_schema => 'SECURITY',
        policy_function => 'EMPLOYEE_SECURITY_POLICY',
        statement_types => 'SELECT,INSERT,UPDATE,DELETE'
    );
END;
/
```

#### Application Context

```sql
-- Create application context
CREATE CONTEXT user_ctx USING security_pkg;

-- Create context package
CREATE OR REPLACE PACKAGE security_pkg IS
    PROCEDURE set_user_context;
END;
/

CREATE OR REPLACE PACKAGE BODY security_pkg IS
    PROCEDURE set_user_context IS
        dept_id NUMBER;
        user_role VARCHAR2(50);
    BEGIN
        -- Get user's department
        SELECT department_id INTO dept_id
        FROM hr.employees
        WHERE employee_id = SYS_CONTEXT('USERENV', 'CLIENT_IDENTIFIER');

        -- Set context values
        DBMS_SESSION.SET_CONTEXT('USER_CTX', 'DEPT_ID', dept_id);
        DBMS_SESSION.SET_CONTEXT('USER_CTX', 'USER_ROLE', user_role);
    END;
END;
/

-- Create logon trigger to set context
CREATE OR REPLACE TRIGGER set_user_context_trigger
    AFTER LOGON ON DATABASE
BEGIN
    security_pkg.set_user_context;
END;
/
```

### Fine-Grained Access Control

#### Column-Level Security

```sql
-- Create column masking policy
CREATE OR REPLACE FUNCTION mask_ssn_policy(
    schema_var IN VARCHAR2,
    table_var IN VARCHAR2
) RETURN VARCHAR2 IS
BEGIN
    IF SYS_CONTEXT('USERENV', 'SESSION_USER') != 'HR_MANAGER' THEN
        RETURN 'ssn = ''XXX-XX-'' || SUBSTR(ssn, -4)';
    END IF;
    RETURN NULL;
END;
/

-- Apply column masking
BEGIN
    DBMS_RLS.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        policy_name => 'SSN_MASKING_POLICY',
        function_schema => 'SECURITY',
        policy_function => 'MASK_SSN_POLICY',
        statement_types => 'SELECT',
        sec_relevant_cols => 'SSN',
        sec_relevant_cols_opt => DBMS_RLS.ALL_ROWS
    );
END;
/
```

## ü"' Data Encryption

### Transparent Data Encryption (TDE)

#### Wallet Management

```sql
-- Create wallet directory
mkdir -p /opt/oracle/wallet

-- Configure wallet location in sqlnet.ora
ENCRYPTION_WALLET_LOCATION =
    (SOURCE = (METHOD = FILE)
     (METHOD_DATA =
       (DIRECTORY = /opt/oracle/wallet)))

-- Create and open wallet
ALTER SYSTEM SET ENCRYPTION KEY IDENTIFIED BY "WalletPassword123!";

-- Open wallet
ALTER SYSTEM SET ENCRYPTION WALLET OPEN IDENTIFIED BY "WalletPassword123!";

-- Check wallet status
SELECT wrl_parameter, status, wallet_type
FROM v$encryption_wallet;
```

#### Column Encryption

```sql
-- Create table with encrypted columns
CREATE TABLE customers (
    customer_id NUMBER,
    customer_name VARCHAR2(100),
    ssn VARCHAR2(11) ENCRYPT USING 'AES256',
    credit_card VARCHAR2(16) ENCRYPT USING 'AES256' SALT,
    email VARCHAR2(100)
);

-- Add encryption to existing column
ALTER TABLE customers MODIFY (phone_number ENCRYPT USING 'AES256');

-- Remove encryption
ALTER TABLE customers MODIFY (phone_number DECRYPT);
```

#### Tablespace Encryption

```sql
-- Create encrypted tablespace
CREATE TABLESPACE secure_data
DATAFILE '/opt/oracle/oradata/secure_data01.dbf' SIZE 100M
ENCRYPTION USING 'AES256'
DEFAULT STORAGE(ENCRYPT);

-- Encrypt existing tablespace
ALTER TABLESPACE users ENCRYPTION ONLINE USING 'AES256' ENCRYPT;

-- Check tablespace encryption
SELECT tablespace_name, encrypted
FROM dba_tablespaces;
```

### Network Encryption

#### Oracle Net Encryption

```sql
-- Configure sqlnet.ora for encryption
SQLNET.ENCRYPTION_SERVER = REQUIRED
SQLNET.ENCRYPTION_TYPES_SERVER = (AES256, AES192, AES128)
SQLNET.CRYPTO_CHECKSUM_SERVER = REQUIRED
SQLNET.CRYPTO_CHECKSUM_TYPES_SERVER = (SHA256, SHA1)

-- Configure client-side encryption
SQLNET.ENCRYPTION_CLIENT = REQUIRED
SQLNET.ENCRYPTION_TYPES_CLIENT = (AES256, AES192, AES128)
```

#### SSL/TLS Configuration

```sql
-- Configure SSL in listener.ora
LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = TCPS)(HOST = dbserver)(PORT = 2484))
    )
  )

SSL_CLIENT_AUTHENTICATION = FALSE
WALLET_LOCATION =
  (SOURCE =
    (METHOD = FILE)
    (METHOD_DATA =
      (DIRECTORY = /opt/oracle/wallet)
    )
  )

-- Configure SSL in tnsnames.ora
ORCL_SSL =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCPS)(HOST = dbserver)(PORT = 2484))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = orcl)
    )
    (SECURITY =
      (SSL_SERVER_CERT_DN = "CN=dbserver,OU=IT,O=Company,C=US")
    )
  )
```

### Data Redaction

#### Full Redaction

```sql
-- Create redaction policy for full masking
BEGIN
    DBMS_REDACT.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        policy_name => 'SSN_REDACTION_POLICY',
        column_name => 'SSN',
        function_type => DBMS_REDACT.FULL,
        expression => 'SYS_CONTEXT(''USERENV'', ''SESSION_USER'') != ''HR_MANAGER'''
    );
END;
/
```

#### Partial Redaction

```sql
-- Partial redaction for credit card numbers
BEGIN
    DBMS_REDACT.ADD_POLICY(
        object_schema => 'SALES',
        object_name => 'CUSTOMERS',
        policy_name => 'CC_PARTIAL_REDACTION',
        column_name => 'CREDIT_CARD',
        function_type => DBMS_REDACT.PARTIAL,
        function_parameters => 'VVVVVVVVVVVVFFF,VVVV-VVVV-VVVV-,*,1,12',
        expression => 'SYS_CONTEXT(''USERENV'', ''SESSION_USER'') != ''PAYMENT_PROCESSOR'''
    );
END;
/
```

#### Regular Expression Redaction

```sql
-- Email redaction using regular expressions
BEGIN
    DBMS_REDACT.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        policy_name => 'EMAIL_REGEX_REDACTION',
        column_name => 'EMAIL',
        function_type => DBMS_REDACT.REGEXP,
        regexp_pattern => '([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})',
        regexp_replace_string => 'XXXX@\2',
        expression => 'SYS_CONTEXT(''USERENV'', ''SESSION_USER'') NOT IN (''HR_ADMIN'', ''PAYROLL_ADMIN'')'
    );
END;
/
```

## üåê Network Security

### Connection Security

#### Connection Filtering

```sql
-- Configure connection filtering in sqlnet.ora
TCP.INVITED_NODES = (192.168.1.*, 10.0.0.*)
TCP.EXCLUDED_NODES = (192.168.1.100)

-- Configure valid node checking
TCP.VALIDNODE_CHECKING = YES
```

#### Connection Pooling Security

```sql
-- Configure DRCP (Database Resident Connection Pooling)
EXEC DBMS_CONNECTION_POOL.START_POOL();

-- Configure connection timeout
EXEC DBMS_CONNECTION_POOL.ALTER_PARAM(
    'MINSIZE', '5');
EXEC DBMS_CONNECTION_POOL.ALTER_PARAM(
    'MAXSIZE', '100');
EXEC DBMS_CONNECTION_POOL.ALTER_PARAM(
    'INCRSIZE', '10');
```

### Firewall Integration

#### Oracle Connection Manager

```sql
-- Configure Connection Manager (cman.ora)
CMAN = (ADDRESS_LIST =
    (ADDRESS = (PROTOCOL=tcp)(HOST=cman-server)(PORT=1521))
)

CMAN_ADMIN = (ADDRESS = (PROTOCOL=tcp)(HOST=cman-server)(PORT=1830))

PARAMETER_LIST = (
    (CONNECTION_STATISTICS=yes)
    (LOG_LEVEL=2)
    (MAX_GATEWAY_PROCESSES=8)
    (MIN_GATEWAY_PROCESSES=3)
)

CMAN_RULES = (
    (RULE = (SRC=192.168.1.*)(DST=dbserver)(SRV=orcl)(ACT=accept))
    (RULE = (SRC=*)(DST=*)(SRV=*)(ACT=reject))
)
```

## ü"ä Auditing

### Standard Auditing

#### Database Auditing Configuration

```sql
-- Enable database auditing
ALTER SYSTEM SET audit_trail = DB;

-- Audit specific statements
AUDIT CREATE TABLE BY john_doe;
AUDIT DELETE ON hr.employees;
AUDIT SELECT ON hr.salary_info BY ACCESS;

-- Audit system privileges
AUDIT CREATE USER;
AUDIT DROP USER;
AUDIT ALTER SYSTEM;

-- Audit by session or access
AUDIT UPDATE ON hr.employees BY SESSION;
AUDIT SELECT ON hr.employees BY ACCESS;
```

#### OS Auditing

```sql
-- Configure OS auditing
ALTER SYSTEM SET audit_trail = OS;
ALTER SYSTEM SET audit_file_dest = '/opt/oracle/audit';

-- Audit privileged operations to OS
AUDIT CONNECT BY sys BY ACCESS;
AUDIT ALL STATEMENTS BY sys;
```

### Fine-Grained Auditing (FGA)

#### Creating FGA Policies

```sql
-- Create FGA policy for sensitive data access
BEGIN
    DBMS_FGA.ADD_POLICY(
        object_schema => 'HR',
        object_name => 'EMPLOYEES',
        policy_name => 'SALARY_ACCESS_AUDIT',
        audit_condition => 'SALARY > 100000',
        audit_column => 'SALARY,COMMISSION',
        handler_schema => 'SECURITY',
        handler_module => 'ALERT_PACKAGE.SALARY_ACCESS_ALERT',
        enable => TRUE,
        statement_types => 'SELECT,UPDATE'
    );
END;
/

-- Create alert handler
CREATE OR REPLACE PACKAGE alert_package IS
    PROCEDURE salary_access_alert(
        object_schema VARCHAR2,
        object_name VARCHAR2,
        policy_name VARCHAR2
    );
END;
/

CREATE OR REPLACE PACKAGE BODY alert_package IS
    PROCEDURE salary_access_alert(
        object_schema VARCHAR2,
        object_name VARCHAR2,
        policy_name VARCHAR2
    ) IS
    BEGIN
        -- Send alert email or log to security system
        INSERT INTO security_alerts (
            alert_time,
            username,
            object_accessed,
            policy_violated,
            session_id
        ) VALUES (
            SYSDATE,
            SYS_CONTEXT('USERENV', 'SESSION_USER'),
            object_schema || '.' || object_name,
            policy_name,
            SYS_CONTEXT('USERENV', 'SESSIONID')
        );
        COMMIT;
    END;
END;
/
```

### Unified Auditing

#### Configuring Unified Auditing

```sql
-- Check if unified auditing is enabled
SELECT value FROM v$option WHERE parameter = 'Unified Auditing';

-- Create unified audit policy
CREATE AUDIT POLICY sensitive_data_policy
ACTIONS SELECT, INSERT, UPDATE, DELETE ON hr.employees,
        CREATE TABLE, DROP TABLE,
        ALTER SYSTEM
WHEN 'SYS_CONTEXT(''USERENV'', ''IP_ADDRESS'') NOT LIKE ''192.168.1.%'''
EVALUATE PER SESSION;

-- Enable audit policy
AUDIT POLICY sensitive_data_policy;

-- Audit specific users
AUDIT POLICY sensitive_data_policy BY john_doe, jane_smith;
```

#### Audit Data Analysis

```sql
-- Query unified audit trail
SELECT event_timestamp,
       dbusername,
       action_name,
       object_schema,
       object_name,
       sql_text,
       client_program_name,
       client_hostname
FROM unified_audit_trail
WHERE event_timestamp >= SYSDATE - 1
ORDER BY event_timestamp DESC;

-- Analyze failed login attempts
SELECT dbusername,
       client_hostname,
       COUNT(*) as failed_attempts,
       MIN(event_timestamp) as first_attempt,
       MAX(event_timestamp) as last_attempt
FROM unified_audit_trail
WHERE action_name = 'LOGON'
  AND return_code != 0
  AND event_timestamp >= SYSDATE - 1
GROUP BY dbusername, client_hostname
HAVING COUNT(*) > 5
ORDER BY failed_attempts DESC;
```

## ü"ß Advanced Security Features

### Oracle Database Vault

#### Database Vault Components

```sql
-- Enable Database Vault
EXEC DBMS_MACADM.ENABLE_DV;

-- Create realm to protect HR schema
EXEC DBMS_MACADM.CREATE_REALM(
    realm_name => 'HR Protection Realm',
    description => 'Protects HR schema from unauthorized access',
    enabled => DBMS_MACUTL.G_YES,
    audit_options => DBMS_MACUTL.G_REALM_AUDIT_FAIL,
    realm_type => 1
);

-- Add objects to realm
EXEC DBMS_MACADM.ADD_OBJECT_TO_REALM(
    realm_name => 'HR Protection Realm',
    object_owner => 'HR',
    object_name => '%',
    object_type => '%'
);

-- Authorize users for realm
EXEC DBMS_MACADM.ADD_AUTH_TO_REALM(
    realm_name => 'HR Protection Realm',
    grantee => 'HR_MANAGER',
    rule_set_name => 'Business Hours Rule Set',
    auth_options => DBMS_MACUTL.G_REALM_AUTH_OWNER
);
```

#### Command Rules

```sql
-- Create command rule to restrict ALTER SYSTEM
EXEC DBMS_MACADM.CREATE_COMMAND_RULE(
    command => 'ALTER SYSTEM',
    rule_set_name => 'DBA Rule Set',
    object_owner => '%',
    object_name => '%',
    enabled => DBMS_MACUTL.G_YES
);

-- Create rule set with time restrictions
EXEC DBMS_MACADM.CREATE_RULE_SET(
    rule_set_name => 'Business Hours Rule Set',
    description => 'Allows access only during business hours',
    enabled => DBMS_MACUTL.G_YES,
    eval_options => DBMS_MACUTL.G_RULESET_EVAL_ALL,
    audit_options => DBMS_MACUTL.G_RULESET_AUDIT_FAIL,
    fail_options => DBMS_MACUTL.G_RULESET_FAIL_SILENT,
    fail_message => 'Access denied outside business hours',
    fail_code => -20001
);

-- Create rule for business hours
EXEC DBMS_MACADM.CREATE_RULE(
    rule_name => 'Business Hours Rule',
    rule_expr => 'TO_NUMBER(TO_CHAR(SYSDATE, ''HH24'')) BETWEEN 8 AND 18
                  AND TO_CHAR(SYSDATE, ''DY'') NOT IN (''SAT'', ''SUN'')'
);

-- Add rule to rule set
EXEC DBMS_MACADM.ADD_RULE_TO_RULE_SET(
    rule_set_name => 'Business Hours Rule Set',
    rule_name => 'Business Hours Rule'
);
```

### Oracle Label Security (OLS)

#### OLS Configuration

```sql
-- Enable Label Security
EXEC LBACSYS.CONFIGURE_OLS;
EXEC LBACSYS.OLS_ENFORCEMENT.ENABLE_OLS;

-- Create policy
EXEC SA_SYSDBA.CREATE_POLICY(
    policy_name => 'DOCUMENT_POLICY',
    column_name => 'DOCUMENT_LABEL'
);

-- Create levels
EXEC SA_COMPONENTS.CREATE_LEVEL(
    policy_name => 'DOCUMENT_POLICY',
    level_num => 100,
    short_name => 'PUB',
    long_name => 'PUBLIC'
);

EXEC SA_COMPONENTS.CREATE_LEVEL(
    policy_name => 'DOCUMENT_POLICY',
    level_num => 200,
    short_name => 'INT',
    long_name => 'INTERNAL'
);

EXEC SA_COMPONENTS.CREATE_LEVEL(
    policy_name => 'DOCUMENT_POLICY',
    level_num => 300,
    short_name => 'CON',
    long_name => 'CONFIDENTIAL'
);

-- Create compartments
EXEC SA_COMPONENTS.CREATE_COMPARTMENT(
    policy_name => 'DOCUMENT_POLICY',
    comp_num => 10,
    short_name => 'HR',
    long_name => 'HUMAN_RESOURCES'
);

EXEC SA_COMPONENTS.CREATE_COMPARTMENT(
    policy_name => 'DOCUMENT_POLICY',
    comp_num => 20,
    short_name => 'FIN',
    long_name => 'FINANCE'
);

-- Apply policy to table
EXEC SA_POLICY_ADMIN.APPLY_TABLE_POLICY(
    policy_name => 'DOCUMENT_POLICY',
    schema_name => 'DOCUMENTS',
    table_name => 'SENSITIVE_DOCS',
    table_options => 'READ_CONTROL,WRITE_CONTROL'
);

-- Set user labels
EXEC SA_USER_ADMIN.SET_USER_LABELS(
    policy_name => 'DOCUMENT_POLICY',
    user_name => 'JOHN_DOE',
    max_read_label => 'CON:HR,FIN',
    max_write_label => 'INT:HR',
    min_write_label => 'PUB',
    def_label => 'INT:HR',
    row_label => 'INT:HR'
);
```

### Privilege Analysis

#### Capturing Privilege Usage

```sql
-- Create privilege analysis policy
EXEC DBMS_PRIVILEGE_CAPTURE.CREATE_CAPTURE(
    name => 'APP_PRIVILEGE_ANALYSIS',
    description => 'Analyze application privilege usage',
    type => DBMS_PRIVILEGE_CAPTURE.G_DATABASE
);

-- Start capture
EXEC DBMS_PRIVILEGE_CAPTURE.START_CAPTURE('APP_PRIVILEGE_ANALYSIS');

-- Run application workload...

-- Stop capture
EXEC DBMS_PRIVILEGE_CAPTURE.STOP_CAPTURE('APP_PRIVILEGE_ANALYSIS');

-- Generate results
EXEC DBMS_PRIVILEGE_CAPTURE.GENERATE_RESULT('APP_PRIVILEGE_ANALYSIS');

-- Analyze unused privileges
SELECT username,
       sys_priv,
       used_flag
FROM dba_unused_sysprivs
WHERE capture = 'APP_PRIVILEGE_ANALYSIS'
  AND used_flag = 0;

-- Analyze unused object privileges
SELECT username,
       object_owner,
       object_name,
       obj_priv,
       used_flag
FROM dba_unused_objprivs
WHERE capture = 'APP_PRIVILEGE_ANALYSIS'
  AND used_flag = 0;
```

## ü"ã Security Best Practices

### Password Security

- Use strong, complex passwords
- Implement password policies
- Regular password rotation
- Avoid default passwords
- Use password verification functions

### Access Control

- Implement least privilege principle
- Use roles instead of direct grants
- Regular access reviews
- Separate REDACTED_LDAP_BIND_PASSWORDistrative duties
- Monitor privileged access

### Data Protection

- Encrypt sensitive data at rest
- Encrypt data in transit
- Implement data masking for non-production
- Use data redaction for sensitive queries
- Regular security assessments

### Monitoring and Alerting

- Enable comprehensive auditing
- Monitor failed login attempts
- Alert on suspicious activities
- Regular security log reviews
- Automated threat detection

---

**Last Updated**: December 2024
**Version**: 1.0
**Maintainer**: Oracle Core Shared Team
