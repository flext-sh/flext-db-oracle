<!-- Generated from docs/guides/getting-started.md for flext-db-oracle. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-db-oracle - Getting Started with FLEXT

> Project profile: `flext-db-oracle`

<!-- TOC START -->
- [What is FLEXT](#what-is-flext)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Basic Installation](#basic-installation)
  - [Development Installation](#development-installation)
  - [Docker Installation](#docker-installation)
- [Your First FLEXT Application](#your-first-flext-application)
  - [1. Basic Setup](#1-basic-setup)
  - [2. Using flext-ldif for LDIF Processing](#2-using-flext-ldif-for-ldif-processing)
  - [3. Railway-Oriented Error Handling](#3-railway-oriented-error-handling)
  - [4. CQRS Pattern with Commands and Queries](#4-cqrs-pattern-with-commands-and-queries)
- [Configuration](#configuration)
  - [Basic Configuration](#basic-configuration)
  - [Programmatic Configuration](#programmatic-configuration)
- [Next Steps](#next-steps)
  - [Explore the Ecosystem](#explore-the-ecosystem)
  - [Learn Key Patterns](#learn-key-patterns)
  - [Build Real Applications](#build-real-applications)
- [Getting Help](#getting-help)
- [What's Next](#whats-next)
<!-- TOC END -->

## What is FLEXT

FLEXT is an enterprise-grade data integration platform built with Python 3.13+ and modern architectural patterns. It provides:

- **Unified API**: Single facade pattern across all libraries
- **Type Safety**: Full Pydantic v2 integration
- **Enterprise Patterns**: CQRS, Railway-oriented programming, Dependency Injection
- **Extensible**: Plugin architecture with flext-core patterns
- **Current**: Comprehensive testing, monitoring, and error handling

## Prerequisites

- **Python 3.13+**: FLEXT requires Python 3.13 or higher
- **pip**: For package installation
- **virtualenv** (recommended): For isolated environments

## Installation

### Basic Installation

Install FLEXT core and commonly used libraries:

```bash
# Install core framework
pip install flext-core

# Install LDIF processing (most common use case)
pip install flext-ldif

# Install additional libraries as needed
pip install flext-api flext-auth flext-ldap
```

### Development Installation

For development and testing:

```bash
# Clone the repository
git clone https://github.com/flext-sh/flext.git
cd flext

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Docker Installation

For containerized deployments:

```bash
# Build FLEXT image
docker build -t flext:latest -f docker/Dockerfile .

# Run FLEXT container
docker run -v $(pwd)/data:/app/data flext:latest
```

## Your First FLEXT Application

### 1. Basic Setup

```python
from flext_cli import u
from flext_core import FlextContainer

# Create dependency injection container
container = FlextContainer()

# Register services (example)
# container.bind("IService", ServiceImplementation())

u.Cli.info("FLEXT application initialized!")
```

### 2. Using flext-ldif for LDIF Processing

```python
from flext_cli import u
from flext_ldif import ldif

ldif_content = """dn: cn=test,dc=example,dc=com
cn: test
sn: user
objectClass: inetOrgPerson"""

result = ldif.parse_string(ldif_content)
if result.success:
    entries = result.value.entries
    u.Cli.info(f"Successfully parsed {len(entries)} LDIF entries")
else:
    u.Cli.info(f"Failed to parse LDIF: {result.error}")
```

### 3. Railway-Oriented Error Handling

```python
from __future__ import annotations
from flext_cli import u
from flext_core import p, r
from flext_ldif import ldif


def process_ldif_data(content: str) -> p.Result[str]:
    # Parse LDIF
    parse_result = ldif.parse_string(content)
    if parse_result.failure:
        return r[str].fail(parse_result.error or "LDIF parse failed")

    entries = parse_result.value.entries

    # Process entries
    try:
        processed_data = process_entries(entries)
        return r[str].ok(processed_data)
    except Exception as e:
        return r[str].fail(str(e))


def process_entries(entries: list) -> str:
    # Your processing logic here
    return f"Processed {len(entries)} entries"


ldif_content = """dn: cn=test,dc=example,dc=com
cn: test
sn: user
objectClass: inetOrgPerson"""

result = process_ldif_data(ldif_content)
if result.success:
    u.Cli.info(f"Success: {result.unwrap()}")
else:
    u.Cli.info(f"Error: {result.error}")
```

### 4. CQRS Pattern with Commands and Queries

```python
from __future__ import annotations
from flext_cli import u
from flext_core import FlextDispatcher, p, r


class CreateUserCommand:
    command_type = "create_user"

    def __init__(self, username: str, email: str) -> None:
        self.username = username
        self.email = email


class GetUserQuery:
    query_type = "get_user"

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


class CreateUserHandler:
    message_type = "create_user"

    def __call__(self, cmd: CreateUserCommand) -> r[str]:
        # Create user logic
        return r[str].ok(f"User {cmd.username} created")


class GetUserHandler:
    message_type = "get_user"

    def __call__(self, query: GetUserQuery) -> r[str]:
        # Get user logic
        return r[str].ok(f"User {query.user_id} data")


# Setup dispatcher
dispatcher = FlextDispatcher()
dispatcher.register_handler(CreateUserHandler())
dispatcher.register_handler(GetUserHandler())

# Use the dispatcher
create_result = dispatcher.dispatch(CreateUserCommand("john", "john@example.com"))
get_result = dispatcher.dispatch(GetUserQuery("user123"))

u.Cli.info(f"Create result: {create_result.unwrap()}")
u.Cli.info(f"Get result: {get_result.unwrap()}")
```

## Configuration

### Basic Configuration

FLEXT uses environment variables for configuration:

```bash
# Set configuration
export FLEXT_LOG_LEVEL=INFO
export FLEXT_LDIF_DEFAULT_ENCODING=utf-8
export FLEXT_LDIF_STRICT_VALIDATION=true
```

### Programmatic Configuration

```python
from flext_cli import u
from flext_ldif import FlextLdif, FlextLdifSettings

# Create custom configuration
settings = FlextLdifSettings(
    ldif={"ldif_encoding": "utf-8", "ldif_strict_validation": True}
)

# Use configuration
ldif_api = FlextLdif(settings=settings)

u.Cli.info(
    f"LDIF API configured with encoding: {ldif_api.runtime_settings.ldif.ldif_encoding}"
)
```

## Next Steps

### Explore the Ecosystem

1. **flext-core**: Master the core patterns and abstractions
1. **flext-ldif**: Learn LDIF processing and migration
1. **flext-api**: Build REST APIs with FLEXT
1. **flext-auth**: Implement authentication and authorization
1. **flext-ldap**: Integrate with LDAP servers

### Learn Key Patterns

- **Railway-Oriented Programming**: Functional error handling
- **CQRS**: Command Query Responsibility Segregation
- **Dependency Injection**: Managing component dependencies
- **Domain Events**: Event-driven architecture

### Build Real Applications

- **Data Migration**: Migrate LDIF data between LDAP servers
- **API Development**: Create REST APIs with automatic documentation
- **Data Processing**: Build data pipelines with FLEXT patterns
- **Enterprise Integration**: Connect with existing enterprise systems

## Getting Help

- 📖 **Documentation**: Browse the complete documentation
- 🐛 **Issues**: Report bugs and request features
- 💬 **Discussions**: Ask questions and share knowledge
- 📧 **Support**: Contact the development team

## What's Next

Now that you have FLEXT installed and running, explore these areas:

1. **Architecture Guide**: Understand FLEXT's design principles
1. **API Reference**: Complete API documentation
1. **Project Guides**: Deep dive into specific libraries
1. **Examples**: Real-world usage examples

Happy coding with FLEXT! 🚀
