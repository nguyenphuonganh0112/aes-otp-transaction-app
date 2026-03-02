# AES-OTP Secure Transaction App

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)
![Security](https://img.shields.io/badge/security-AES%20%2B%20OTP-green)
![Status](https://img.shields.io/badge/build-manual-lightgrey)

A Python Tkinter desktop application that simulates a secure electronic transaction system using **AES encryption** and **OTP-based two-factor authentication (2FA)**.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Security Design](#security-design)
- [Secure Transaction Workflow](#secure-transaction-workflow)

---

## Overview

This project demonstrates a secure electronic transaction workflow combining AES encryption and OTP-based two-factor authentication (2FA).

Unlike basic encryption demos, this system introduces a dynamic key derivation mechanism, where the AES encryption key is deterministically derived from the user’s password using SHA-256. This design eliminates the need to store static encryption keys and reduces the risk of centralized key exposure.

The transaction flow includes:

1. User registration → credentials are hashed using SHA-256 before storage.

2. During login, the system verifies hashed credentials and derives an AES key from the user’s password.

3. The transaction amount is encrypted using AES (CBC mode) with a dynamically generated key.

4. A 6-digit OTP is generated, encrypted with AES, and delivered via email.

5. The user must submit the encrypted OTP within 180 seconds to complete verification.

6. The system limits authentication attempts to enhance security.

This architecture demonstrates a user-specific encryption model, where each transaction is protected by a password-derived key combined with time-limited OTP verification.

---

## Features
- SHA-256 hashing for email & password storage
- AES encryption (CBC mode) for transaction amount
- OTP generation + email delivery (SMTP)
- 180-second countdown timer (OTP expiration)
- Lock after 3 failed login attempts
- Sender/Receiver GUI tabs in Tkinter

---

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Quick Start
1) Set environment variables (Windows CMD)

```bash
set SENDER_EMAIL=your_email@gmail.com
set SENDER_PASSWORD=your_app_password
```
2) Run the app
```bash
python main.py
```

---

## Security Design
1. Credential Protection

User email and password are hashed using SHA-256

No plaintext credentials are stored

2. Transaction Encryption

Transaction amount is encrypted using AES (CBC mode)

Encryption key is derived from SHA-256(password)

A random IV (Initialization Vector) is generated for each encryption

3. OTP Verification

6-digit OTP generated randomly

OTP encrypted using AES before being sent via email

OTP expires after 180 seconds

Maximum 3 failed attempts allowed

---

## Secure Transaction Workflow

![System Workflow](assets/system_workflow.png)
