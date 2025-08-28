# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-08-28

### Added
- Comprehensive documentation suite in `docs/` directory

### Changed
- **BREAKING**: Constructor now accepts `metadata` parameter instead of `base`
  - Old: `SQLAlchemyStorage(sessionmaker=session, metadata=Base)`
  - New: `SQLAlchemyStorage(sessionmaker=session, metadata=Base.metadata)`
  - Passing `Base` object is still supported but deprecated with warning
- Improved integration with SQLAlchemy ORM
- Enhanced metadata handling for better table creation and migration support
- More robust session management

### Fixed
- Fixed table creation
- Resolved database session lifecycle management
- Fixed JSON serialization edge cases

### Deprecated
- Passing `Base` object to `metadata` parameter (use `Base.metadata` instead)

### Documentation
- Added comprehensive setup and usage documentation

## [0.1.1] - 2025-01-30

### Added
- Initial release attempt

### Issues
- **CRITICAL**: Non-functional release due to multiple compatibility issues
- Database connection problems
- FSM integration failures
- Missing required dependencies
- Incomplete implementation

**Note**: This version should not be used. Please upgrade to 0.2.0 or later.
