import { createClient } from "@supabase/supabase-js"

const SUPABASE_URL = "https://gzalfhvizdcdrycdqgqx.supabase.co"
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6YWxmaHZpemRjZHJ5Y2RxZ3F4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg0Njk4NTgsImV4cCI6MjA5NDA0NTg1OH0.osN7EvVG3cWBAY5c87hrlQC4BrTDrrXsHtC1BwO_UHM"

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)