# Aspire

[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square)](https://github.com/nemmons/aspire/blob/main/LICENSE)
![Github Actions](https://github.com/nemmons/aspire/workflows/build/badge.svg)
[![codecov](https://codecov.io/gh/nemmons/aspire/branch/main/graph/badge.svg?token=Q9SN60QZ5L)](https://codecov.io/gh/nemmons/aspire)
[![CodeFactor](https://www.codefactor.io/repository/github/nemmons/aspire/badge)](https://www.codefactor.io/repository/github/nemmons/aspire)
[![Requirements Status](https://requires.io/github/nemmons/aspire/requirements.svg?branch=main)](https://requires.io/github/nemmons/aspire/requirements/?branch=main)

#### Description

**A** **S**imple **P**ython **I**nsurance **R**ating **E**ngine. Configure your insurance rating algorithm(s), provide your rating factors, and generate insurance rates via an web UI or batch-rate a CSV. For background on insurance manuals/rating, see Chapter 2 of [this Ratemaking guide (pdf)](https://www.casact.org/library/studynotes/werner_modlin_ratemaking.pdf) from the Casualty Actuary Society.

#### Note

This project is early in development. The core functionality is working and a working demo is included, but the Flask webserver portion has not been hardened for production use. Use caution!

#### Installation
*More detail coming soon, along with an optional Docker config for easier startup!*

1. Clone this repository.
1. (Recommended) Initialize a virtual environment in the project root.
1. Install dependencies (python, pip, `pip install -r requirements.txt`).
1. (If not using SQLite) Install appropriate dependencies to support the SQLAlchemy connection to your database of choice (see [here](https://docs.sqlalchemy.org/en/13/core/engines.html#supported-databases) for direction).
1. Configure the application's database connection: Create `config.yml` (using `config.yml.example` as a template) in `aspire/app/database/` and set the appropriate connection string.

#### Features

- [X] Batch Rating 
- [ ] Web UI for rating configuration
