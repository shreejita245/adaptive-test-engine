// Central API configuration — change this ONE place for local vs production
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"

export const API = isLocal
  ? "http://127.0.0.1:8000"
  : "https://adaptive-test-engine-production.up.railway.app"
