import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to query NexaGraph ");
      }

      const data = await response.json();
      setResult(data.answer);
    } catch (err) {
      setError(
        "Could not connect to the NexaGraph API. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="logo">NG</div>

          <div>
            <h1>NexaGraph</h1>
            <p>Enterprise GraphRAG Knowledge Intelligence Platform</p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Local AI
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="badge">Enterprise GraphRAG Knowledge Intelligence</div>

          <h2>
            Ask your documents.
            <br />
            <span>Get grounded answers.</span>
          </h2>

          <p className="hero-text">
            Search across enterprise documents using hybrid retrieval,
            semantic reranking, and knowledge-graph context.
          </p>
        </section>

        <section className="query-card">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the Siemens reports..."
            rows={4}
          />

          <div className="query-footer">
            <span>Press Enter to ask</span>

            <button
              onClick={askQuestion}
              disabled={loading || !question.trim()}
            >
              {loading ? "Thinking..." : "Ask NexaGraph →"}
            </button>
          </div>
        </section>

        {error && <div className="error">{error}</div>}

        {result && (
          <section className="result-card">
            <div className="result-header">
              <h3>Answer</h3>
              <span className="grounded">Grounded response</span>
            </div>

            <p className="answer">{result.answer}</p>

            {result.citations?.length > 0 && (
              <div className="citations">
                <h4>Sources</h4>

                {result.citations.map((citation, index) => (
                  <div className="citation" key={index}>
                    <div>
                      <strong>
                        {citation.document.replaceAll("_", " ")}
                      </strong>

                      <span>
                        Page {citation.page}
                      </span>
                    </div>

                    <div className="citation-score">
                      Relevance {citation.rerank_score.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {!result && !loading && (
          <section className="examples">
            <p>Try asking:</p>

            <button
              onClick={() =>
                setQuestion(
                  "Wie hoch war der Umsatz von Siemens im Geschäftsjahr 2025?"
                )
              }
            >
              What was Siemens' revenue in 2025?
            </button>

            <button
              onClick={() =>
                setQuestion(
                  "Wie häufig tagte der Aufsichtsrat im Geschäftsjahr 2025?"
                )
              }
            >
              How often did the Supervisory Board meet?
            </button>

            <button
              onClick={() =>
                setQuestion(
                  "Welche drei Impact Areas stehen im Mittelpunkt des Nachhaltigkeitsberichts?"
                )
              }
            >
              What are the sustainability impact areas?
            </button>
          </section>
        )}
      </main>

      <footer>
        <span>NexaGraph</span>
        <span>Local & Open Source AI Stack</span>
      </footer>
    </div>
  );
}

export default App;