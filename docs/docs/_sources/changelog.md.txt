# ScraperV4 Changelog

All notable changes to ScraperV4 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.1] - 2025-01-20

### Fixed
- **CRITICAL FIX: Playwright Interactive Mode Launch Failure**
  - Resolved issue where Playwright Interactive Mode would fail to launch with empty error objects `{}`
  - **Root Cause**: Missing frontend API methods in `ScraperAPI` class (`/web/static/js/api.js`)
  - **Impact**: Playwright Interactive Mode was completely non-functional for all users
  - **Solution**: Added all 11 required Playwright API methods to the frontend `ScraperAPI` class
  - **Affected Methods Added**:
    - `startPlaywrightInteractive(url, options)`
    - `getBrowserScreenshot(sessionId, fullPage)`
    - `startElementSelection(sessionId)`
    - `stopElementSelection(sessionId)`
    - `selectElementAtCoordinates(sessionId, x, y)`
    - `getSelectedElements(sessionId)`
    - `closePlaywrightSession(sessionId)`
    - `getPageInfo(sessionId)`
    - `closeInteractiveSession(sessionId)`
    - `getActiveInteractiveSessions()`
    - `createTemplateFromSelections(sessionId, templateName, templateDescription)`

### Technical Details
- **Files Modified**: `/web/static/js/api.js`
- **Dependencies Verified**: Playwright v1.54.0, playwright-stealth v2.0.0, Chromium browser binaries
- **Backend Status**: All corresponding `@eel.expose` endpoints were already properly implemented
- **Testing**: Verified with multiple test URLs including `https://books.toscrape.com`

### Migration Notes
- **No action required for existing users** - this is a bug fix, not a breaking change
- Users who previously experienced Playwright launch failures should now have full functionality
- All existing templates and configurations remain unchanged

### Diagnostic Information
- **Symptoms Resolved**: 
  - "Error starting Playwright interactive mode: {}" messages
  - `TypeError: window.api.startPlaywrightInteractive is not a function` console errors
  - Interactive mode buttons producing no visible response
- **Verification**: Run `console.log(typeof window.api.startPlaywrightInteractive)` in browser console - should now return `"function"`

### Documentation Added
- **New**: [Playwright Interactive Mode Troubleshooting Guide](troubleshooting/playwright-interactive-issues.md)
- **New**: [Frontend API Integration Fix Guide](how-to/fix-playwright-api-integration.md)
- **New**: [Frontend API Reference](reference/api/frontend-api.md)
- **Updated**: [Main Troubleshooting Guide](tutorials/troubleshooting.md) - Added Part 9: Playwright Issues
- **Updated**: [Playwright Architecture Documentation](explanations/playwright-architecture.md)

---

## [4.1.0] - 2025-01-15

### Added
- **Playwright Interactive Mode** - Revolutionary visual template creation without CORS restrictions
  - Real browser automation using Playwright instead of iframe embedding
  - Universal website compatibility - works on all sites regardless of security headers
  - Visual element selection with real-time highlighting and feedback
  - Anti-detection capabilities with browser fingerprint randomization
  - Advanced selector generation with quality scoring and fallbacks
  - Complete session management with screenshot streaming

- **New Interactive Architecture**
  - `PlaywrightInteractiveService` - Backend browser automation service
  - `interactive_overlay.js` - JavaScript overlay for element selection
  - 11 new API endpoints for complete Playwright integration
  - Session-based browser management with cleanup capabilities

### Enhanced
- **Template Creation Workflow**
  - Point-and-click element selection without writing CSS selectors
  - Real-time template validation and testing
  - Automatic selector optimization and quality assessment
  - Support for complex interactions (forms, pagination, authentication)

- **Documentation Expansion**
  - Comprehensive tutorial for Playwright Interactive Mode
  - Advanced how-to guides with real-world recipes
  - Technical architecture documentation
  - Complete API reference with TypeScript definitions

### Technical Specifications
- **Browser Support**: Chromium, Firefox, Safari (via Playwright)
- **Dependencies**: `playwright>=1.54.0`, `playwright-stealth>=2.0.0`
- **Performance**: ~3-5 second session startup, <1 second screenshot capture
- **Memory Usage**: ~100-200MB per active browser session
- **Concurrent Sessions**: Up to 10 simultaneous sessions (configurable)

---

## [4.0.2] - 2025-01-10

### Fixed
- Fixed Pylance type checking errors across multiple service files
- Resolved `ServiceContainer` missing 'has' method issue
- Fixed async iteration problems in `scraping_service.py`
- Replaced deprecated `datetime.utcnow()` calls with `datetime.now(timezone.utc)`
- Fixed BeautifulSoup HTML extraction from Scrapling responses
- Resolved attribute access issues with safer `getattr()` patterns
- Fixed operator compatibility issues with potentially None values

### Enhanced
- Improved error handling in interactive services
- Better type safety across service layer
- Enhanced logging and debugging capabilities

---

## [4.0.1] - 2025-01-05

### Fixed
- Resolved interactive mode closing behavior
- Fixed Ctrl+R refresh functionality in interactive interface
- Improved UI theme consistency across components
- Enhanced error messaging for better user experience

### Added
- Better session management for interactive features
- Improved cleanup procedures for browser resources

---

## [4.0.0] - 2025-01-01

### Added
- **Complete System Rewrite** - Built from ground up with modern architecture
- **Interactive Template Creation** - Visual element selection interface
- **Advanced Stealth Features** - Multi-layer anti-detection system
- **Enterprise-Grade Performance** - Async processing with real-time monitoring
- **Modern Web Interface** - Responsive UI with real-time updates
- **Comprehensive API** - RESTful endpoints for programmatic access
- **Template Management System** - Advanced template creation, editing, and sharing
- **Multi-Format Export** - JSON, CSV, Excel with custom formatting options
- **Intelligent Proxy Rotation** - Performance-optimized proxy management
- **Real-Time Job Monitoring** - Live progress tracking with detailed metrics

### Technical Foundation
- **Backend**: Python 3.8+ with AsyncIO for concurrent processing
- **Frontend**: Modern HTML5/CSS3/JavaScript with responsive design
- **Communication**: Eel framework for seamless Python-JavaScript integration
- **Dependencies**: Scrapling, Pandas, BeautifulSoup4, Requests
- **Architecture**: Service-oriented design with dependency injection
- **Storage**: JSON-based with optional database integration
- **Logging**: Comprehensive logging with configurable levels

### Breaking Changes
- **Complete API Redesign** - New endpoint structure and response formats
- **Template Format Changes** - Enhanced template schema with advanced features
- **Configuration Updates** - New settings structure and environment variables
- **File Structure** - Reorganized project layout for better maintainability

### Migration Guide
- See [Migration Documentation](docs/migration/v3-to-v4.md) for detailed upgrade instructions
- Automatic template conversion tools provided
- Backward compatibility layer for critical integrations

---

## Development Guidelines

### Version Numbering
- **Major** (X.0.0): Breaking changes, architectural updates
- **Minor** (X.Y.0): New features, enhancements, significant improvements
- **Patch** (X.Y.Z): Bug fixes, security updates, minor improvements

### Change Categories
- **Added**: New features and capabilities
- **Changed**: Modifications to existing functionality
- **Deprecated**: Features marked for removal in future versions
- **Removed**: Features removed from this version
- **Fixed**: Bug fixes and error corrections
- **Security**: Security improvements and vulnerability fixes

### Documentation Standards
- All changes must include relevant documentation updates
- Breaking changes require migration guides
- New features need tutorial and reference documentation
- API changes must update OpenAPI specifications

### Release Process
1. **Development**: Feature development in feature branches
2. **Testing**: Comprehensive testing including integration tests
3. **Documentation**: Complete documentation updates
4. **Review**: Code review and approval process
5. **Release**: Version tagging and deployment
6. **Announcement**: Release notes and communication

---

## Support and Feedback

### Reporting Issues
- **Bug Reports**: Use GitHub Issues with bug report template
- **Feature Requests**: Use GitHub Discussions for feature proposals
- **Security Issues**: Email security concerns to security@scraperv4.dev

### Community Resources
- **Documentation**: [https://docs.scraperv4.dev](https://docs.scraperv4.dev)
- **Community Forum**: [GitHub Discussions](https://github.com/scraperv4/discussions)
- **Discord Server**: [Join our community](https://discord.gg/scraperv4)
- **Example Projects**: [GitHub Examples Repository](https://github.com/scraperv4/examples)

### Contributing
- **Code Contributions**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Documentation**: Help improve our documentation
- **Community Support**: Assist other users in forums and Discord
- **Bug Reports**: Help us identify and reproduce issues

---

*For complete release notes and detailed technical information, visit our [GitHub Releases](https://github.com/scraperv4/releases) page.*