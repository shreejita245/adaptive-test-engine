import { useEffect, useRef } from "react"

// Decode HTML entities like &lt; &gt; &amp; &quot; &#39; so LaTeX works correctly
function decodeHtmlEntities(text) {
  if (!text) return ""
  return text
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/&le;/g, "≤")
    .replace(/&ge;/g, "≥")
    .replace(/&ne;/g, "≠")
    .replace(/&alpha;/g, "α")
    .replace(/&beta;/g, "β")
    .replace(/&pi;/g, "π")
}

function renderMath(rawText) {
  if (!rawText) return ""

  // Decode HTML entities first so LaTeX commands aren't broken
  const text = decodeHtmlEntities(rawText)

  // if already contains katex HTML, just return as-is
  if (text.includes('class="katex"') || text.includes("class='katex'")) {
    return text
  }

  // replace $$...$$ with display math
  let result = text.replace(/\$\$([^$]+)\$\$/g, (match, math) => {
    try {
      return window.katex ? window.katex.renderToString(math.trim(), {
        throwOnError: false,
        displayMode: true,
        output: "html"
      }) : match
    } catch { return match }
  })

  // replace $...$ with inline math
  result = result.replace(/\$([^$\n]+)\$/g, (match, math) => {
    try {
      return window.katex ? window.katex.renderToString(math.trim(), {
        throwOnError: false,
        displayMode: false,
        output: "html"
      }) : match
    } catch { return match }
  })

  return result
}

export default function MathRenderer({ html, style, className }) {
  const ref = useRef(null)

  useEffect(() => {
    if (ref.current) {
      ref.current.innerHTML = renderMath(html || "")
    }
  }, [html])

  return <div ref={ref} style={style} className={className} />
}