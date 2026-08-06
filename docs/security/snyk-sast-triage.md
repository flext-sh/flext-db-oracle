# Triagem Snyk Code (SAST) — flext-sh/flext-db-oracle

Gerado do scan Snyk (dump 2026-08-06). Bead: `mro-adbc`

## Resumo

**17 achados** — critical 0, high 0, medium 2, low 15

| categoria | achados |
|---|---|
| Use of Hardcoded Passwords | 17 |

## Como usar este documento

Cada achado traz o **código real** extraído da worktree (linha `>>>` = sink reportado), a regra completa e o CWE.
Preencha **Decisão**: `corrigir` / `falso-positivo` (registrar em `.snyk`) / `risco-aceito` (com prazo).

## Achados

### 1 · 🟡 MEDIUM · Use of Hardcoded Passwords
**Local**: `examples/05_simple_working.py:28` · **CWE**: -

```python
       24          settings = FlextDbOracleSettings.model_validate({
       25              "DbOracle": {
       26                  "host": "demo-host",
       27                  "username": "demo-user",
>>>    28                  "password": "demo-password",
       29              }
       30          })
       31          logger.info("✅ Demo configuration created")
       32      return settings
```

**Decisão**: 

### 2 · 🟡 MEDIUM · Use of Hardcoded Passwords
**Local**: `examples/07_sqlalchemy2.py:35` · **CWE**: -

```python
       31              "host": "demo-oracle.example.com",
       32              "port": 1521,
       33              "service_name": "DEMO",
       34              "username": "demo_user",
>>>    35              "password": "demo_password",
       36          }
       37      })
       38  
       39  
```

**Decisão**: 

### 3 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/e2e/test_oracle.py:41` · **CWE**: -

```python
       37                  "host": "nonexistent-host.invalid",
       38                  "port": 9999,
       39                  "service_name": "INVALID_DB",
       40                  "username": "invalid_user",
>>>    41                  "password": "invalid_password",
       42              }
       43          })
       44  
       45      @pytest.fixture
```

**Decisão**: 

### 4 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/integration/test_oracle.py:36` · **CWE**: -

```python
       32              "host": "mock-host",
       33              "port": 1521,
       34              "service_name": "mock-service",
       35              "username": "mock-user",
>>>    36              "password": "mock-pass",
       37          }
       38      })
       39  
       40  
```

**Decisão**: 

### 5 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_api.py:36` · **CWE**: -

```python
       32                  "host": host,
       33                  "port": 19999,
       34                  "service_name": service_name,
       35                  "username": "test_user",
>>>    36                  "password": "test_password",
       37                  "timeout": 1,
       38              }
       39          })
       40  
```

**Decisão**: 

### 6 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_cli.py:229` · **CWE**: -

```python
      225                      "host": "param_test_host",
      226                      "port": 1521,
      227                      "service_name": "PARAM_TEST",
      228                      "username": "param_user",
>>>   229                      "password": "param_pass",
      230                  }
      231              })
      232          )
      233          tm.that(api.settings.DbOracle.host, eq="param_test_host")
```

**Decisão**: 

### 7 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_cli.py:265` · **CWE**: -

```python
      261                      "host": "invalid.host",
      262                      "port": 9999,
      263                      "service_name": "INVALID_SERVICE",
      264                      "username": "invalid_user",
>>>   265                      "password": "invalid_password",
      266                  }
      267              })
      268          )
      269          query_result = api.query("SELECT 1 FROM DUAL")
```

**Decisão**: 

### 8 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_config.py:58` · **CWE**: -

```python
       54                  "host": "db.internal",
       55                  "port": 1522,
       56                  "username": "appuser",
       57                  "service_name": "PRODSVC",
>>>    58                  "password": "apppass",
       59              }
       60          })
       61          tm.that(settings.DbOracle.host, eq="db.internal")
       62          tm.that(settings.DbOracle.port, eq=1522)
```

**Decisão**: 

### 9 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_coverage_baseline.py:33` · **CWE**: -

```python
       29                  "host": "localhost",
       30                  "port": 1521,
       31                  "service_name": "TEST",
       32                  "username": "testuser",
>>>    33                  "password": "testpass",
       34              }
       35          })
       36  
       37      @pytest.fixture
```

**Decisão**: 

### 10 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_coverage_baseline.py:65` · **CWE**: -

```python
       61                  "host": "localhost",
       62                  "port": 1521,
       63                  "service_name": "lower_svc",
       64                  "username": "testuser",
>>>    65                  "password": "testpass",
       66              }
       67          })
       68          tm.that(settings.DbOracle.service_name, eq="lower_svc")
       69  
```

**Decisão**: 

### 11 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_coverage_baseline.py:78` · **CWE**: -

```python
       74                  "host": "secure.example.com",
       75                  "port": 2484,
       76                  "service_name": "SECURE_DB",
       77                  "username": "secure_user",
>>>    78                  "password": "secure_pass",
       79                  "ssl_cert_file": "/path/to/cert.pem",
       80              }
       81          })
       82          tm.that(settings.DbOracle.ssl_cert_file, eq="/path/to/cert.pem")
```

**Decisão**: 

### 12 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_dispatcher.py:25` · **CWE**: -

```python
       21          settings = FlextDbOracleSettings.model_validate({
       22              "DbOracle": {
       23                  "host": "test-host",
       24                  "username": "test-user",
>>>    25                  "password": "test-password",
       26              }
       27          })
       28          return FlextDbOracleServices(settings=settings)
       29  
```

**Decisão**: 

### 13 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_models.py:308` · **CWE**: -

```python
      304                  "port": 1522,
      305                  "name": "ORCL",
      306                  "service_name": "ORCLPDB1",
      307                  "username": "app_user",
>>>   308                  "password": "secret123",
      309                  "ssl_server_cert_dn": "CN=oracle.example.com",
      310              }
      311          })
      312          tm.that(settings.DbOracle.host, eq="oracle.example.com")
```

**Decisão**: 

### 14 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_oracle_example.py:275` · **CWE**: -

```python
      271                  "host": "localhost",
      272                  "port": 1521,
      273                  "service_name": "XEPDB1",
      274                  "username": "invalid_user",
>>>   275                  "password": "invalid_password",
      276              }
      277          })
      278          connection = FlextDbOracleServices(settings=invalid_config)
      279          result = connection.connect()
```

**Decisão**: 

### 15 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_services.py:37` · **CWE**: -

```python
       33                  "host": "localhost",
       34                  "port": 1521,
       35                  "service_name": "TEST",
       36                  "username": "testuser",
>>>    37                  "password": "testpass",
       38              }
       39          })
       40  
       41      @pytest.fixture
```

**Decisão**: 

### 16 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_services.py:80` · **CWE**: -

```python
       76                      "host": "127.0.0.1",
       77                      "port": 19999,
       78                      "service_name": "INVALID",
       79                      "username": "invalid",
>>>    80                      "password": "invalid",
       81                      "timeout": 1,
       82                  }
       83              })
       84          )
```

**Decisão**: 

### 17 · ⚪ LOW · Use of Hardcoded Passwords
**Local**: `tests/unit/test_services.py:478` · **CWE**: -

```python
      474                      "host": "127.0.0.1",
      475                      "port": 19999,
      476                      "service_name": "INVALID",
      477                      "username": "invalid",
>>>   478                      "password": "invalid",
      479                      "timeout": 1,
      480                  }
      481              })
      482          )
```

**Decisão**: 

