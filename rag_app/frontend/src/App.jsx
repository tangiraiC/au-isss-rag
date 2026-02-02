import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { queryBackend } from './api'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e, overrideQuery = null) => {
    if (e) e.preventDefault()
    const searchQuery = overrideQuery || query
    if (!searchQuery.trim()) return

    setQuery(searchQuery) // Update input if triggered via click
    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const data = await queryBackend(searchQuery)
      setResponse(data)
    } catch (err) {
      setError("Failed to fetch results. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setQuery('')
    setResponse(null)
    setError(null)
  }

  return (
    <div className="container">
      <div className="disclaimer-banner">
        ⚠️ This is a student project. Not affiliated with American University. Educational purposes only.
      </div>
      <header className="header">
        <h1>iSSS Chat Assistant</h1>
        <p>Ask questions about International Student & Scholar Services</p>
      </header>

      <main>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What are the requirements for OPT?"
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Ask'}
          </button>
        </form>

        {!response && !loading && (
          <div className="suggestions">
            <p>Popular Questions:</p>
            <div className="suggestion-chips">
              <button onClick={() => { setQuery("What is CPT?"); handleSearch({ preventDefault: () => { } }, "What is CPT?"); }} className="chip">What is CPT?</button>
              <button onClick={() => { setQuery("How do I apply for OPT?"); handleSearch({ preventDefault: () => { } }, "How do I apply for OPT?"); }} className="chip">How do I apply for OPT?</button>
              <button onClick={() => { setQuery("Travel signature requirements"); handleSearch({ preventDefault: () => { } }, "Travel signature requirements"); }} className="chip">Travel signature requirements</button>
              <button onClick={() => { setQuery("How to get a Social Security Number?"); handleSearch({ preventDefault: () => { } }, "How to get a Social Security Number?"); }} className="chip">SSN Application</button>
            </div>
          </div>
        )}

        {error && <div className="error">{error}</div>}

        {response && (
          <div className="results">
            <div className="answer-section">
              <h2>Answer</h2>
              <div className="answer-box">
                <ReactMarkdown>{response.answer}</ReactMarkdown>
              </div>
            </div>

            {/* Relevant Documents section removed per user request */}

            <div className="action-buttons">
              <button onClick={handleReset} className="reset-button">
                ← Start New Search
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
