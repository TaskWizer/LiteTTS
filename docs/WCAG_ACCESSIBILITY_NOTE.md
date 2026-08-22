# WCAG 2.1 Accessibility Note

**Date:** 2026-08-22

## Assessment: Not Applicable

### Reason

LiteTTS is a **Text-to-Speech API backend service**, not a traditional web application with a graphical user interface. WCAG 2.1 (Web Content Accessibility Guidelines) applies to:

- Websites and web applications with user-facing interfaces
- Interactive web content
- Digital content consumed by end-users through browsers

### What LiteTTS Is

- **API Service**: Provides REST API endpoints for TTS synthesis
- **No User Interface**: Does not render HTML pages for user interaction
- **Backend Processing**: Text processing and audio generation
- **Programmatic Access**: Intended for developers/tools, not end consumers directly

### Web Dashboard

The one exception is the `/dashboard` endpoint which provides an HTML analytics page. This dashboard is:

- **Internal Tool**: Used for monitoring, not customer-facing
- **Read-Only**: Displays metrics, no interactive forms
- **Technical Users**: Intended for DevOps/developers

### Conclusion

WCAG 2.1 AAA compliance is **not required** for this project because:

1. It's an API service, not a web application
2. No customer-facing web UI exists
3. The dashboard is an internal monitoring tool

### If Dashboard Were Enhanced

Should the dashboard become customer-facing in the future, WCAG 2.1 AA (minimum) would apply. Considerations would include:

- Color contrast ratios (4.5:1 for normal text)
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators
- Form labels and error identification

For reference, see [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/).

---

*This note is for informational purposes only and does not indicate non-compliance with any accessibility requirements.*
