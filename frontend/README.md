# Sales Monitoring, Forecasting, and Performance AI System

A full-stack sales analytics platform built with `Django`, `Django REST Framework`, `React`, and `PostgreSQL`.

This project helps managers and analysts:
- monitor sales performance
- analyze trends across products and regions
- compare forecasted sales against targets
- review alert signals for forecast shortfalls and forecast error

## Features

### Authentication
- user signup
- JWT login
- protected frontend routes
- current user session endpoint

### Sales Dashboard
- KPI summary cards
- sales trends chart
- sales by region chart
- top products chart
- paginated transactions table
- region and product filters

### Forecasting
- daily sales forecast
- moving average baseline
- weighted moving average baseline
- forecast vs actual comparison
- forecast vs target comparison

### Targets
- overall targets
- region targets
- product targets
- salesperson targets

### Alerts
- forecast target shortfall alerts
- high forecast error alerts
- alert rule execution endpoint
- alert listing and filtering
- resolve alert workflow

## Tech Stack

### Backend
- `Python`
- `Django`
- `Django REST Framework`
- `PostgreSQL`
- `Simple JWT`

### Frontend
- `React`
- `Vite`
- `Axios`
- `Recharts`

### Deployment
- backend prepared for `Render`
- frontend prepared for `Cloudflare Pages`
- database prepared for `Neon`

## Project Structure

```text
backend/
  alerts/
  config/
  core/
  forecasting/
  sales/
  targets/

frontend/
  src/
    api/
    components/
    pages/