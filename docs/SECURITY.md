# Security

MAPy aims to be a secure and privacy-friendly tool to extract EXIF metadata from images. To ensure the safety of the users, there are several security measures in place to protect against common vulnerabilities and threats. The main areas of focus are:

-   **CSP**: MAPy enforces a strict Content Security Policy (CSP) to prevent XSS attacks and other code injection vulnerabilities. This helps to prevent malicious scripts from being executed on the client side. **Enabled by default**.

-   **CSRF protection**: MAPy uses Flask-WTF to protect against Cross-Site Request Forgery (CSRF) attacks. This is done by generating a unique token for each submission and validating it on the server side. **Enabled by default**.

-   **Unique Session IDs**: Flask generates a unique session ID for each user session. This ID is used to store session data on the server and is regenerated after each request to prevent session fixation attacks. **Enabled by default**.

-   **SSL/TLS encryption**: MAPy supports SSL/TLS encryption to secure the communication between the client and the server. This is especially important when handling sensitive data such as EXIF metadata. **Optional**.

    > **Note**: For development purposes, you can use a self-signed certificate with the `-a` flag to enable SSL. However, for production, you should use a valid SSL certificate. See the [installation guide](INSTALLATION.md#securing-the-app-with-ssl) for more information.

## Supported Versions

MAPy tries to follow the latest security best practices and recommendations. As such, usually only the latest stable version of the app is supported. If you are using an older version of MAPy, it is recommended to update to the latest version to ensure you have the latest security fixes and improvements.

| Version      | Supported |
| ------------ | --------- |
| 1.0.x        | ✅        |
| < 1.0 (Beta) | ❌        |

## Reporting a Vulnerability

If you discover a security issue in MAPy, please [create an issue](https://github.com/dan-koller/mapy/issues). I take security seriously and will do my best to address the issue promptly.

If you have any contributions or suggestions to improve the security of MAPy, feel free to open a pull request. Your help is greatly appreciated!
