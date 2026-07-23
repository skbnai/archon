// src/components/Quiz/index.js
//
// Embed a scored multiple-choice quiz in any doc page:
//   import Quiz from '@site/src/components/Quiz';
//   <Quiz
//     id="agentic-systems-basics"
//     questions={[{ question: "…", options: ["…", "…", "…"], answer: 1 }]}
//   />
//
// `id` must be globally unique and stable (changing it resets a reader's
// saved best score for that quiz). Best score persists in localStorage.
// See .claude/skills/gamification/SKILL.md for authoring rules.
import React, { useState } from "react";
import { recordQuizAttempt, getQuizzes } from "@site/src/lib/progressStore";
import styles from "./styles.module.css";

export default function Quiz({ id, title = "Check your understanding", questions }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [best, setBest] = useState(() => {
    const existing = getQuizzes()[id];
    return existing ? existing.best : null;
  });

  const allAnswered = questions.every((_, i) => answers[i] !== undefined);
  const score = questions.reduce(
    (sum, q, i) => sum + (answers[i] === q.answer ? 1 : 0),
    0
  );

  function handleSubmit(e) {
    e.preventDefault();
    if (!allAnswered) return;
    setSubmitted(true);
    const result = recordQuizAttempt(id, score, questions.length);
    setBest(result.best);
  }

  function handleRetry() {
    setAnswers({});
    setSubmitted(false);
  }

  return (
    <form className={styles.quiz} onSubmit={handleSubmit}>
      <h4 className={styles.title}>{title}</h4>
      {questions.map((q, qi) => (
        <fieldset key={qi} className={styles.question} disabled={submitted}>
          <legend>{q.question}</legend>
          {q.options.map((opt, oi) => (
            <label key={oi} className={styles.option}>
              <input
                type="radio"
                name={`${id}-q${qi}`}
                checked={answers[qi] === oi}
                onChange={() => setAnswers((a) => ({ ...a, [qi]: oi }))}
              />
              <span>{opt}</span>
              {submitted && oi === q.answer && (
                <span className={styles.correct}> ✓ correct</span>
              )}
            </label>
          ))}
        </fieldset>
      ))}

      {!submitted ? (
        <button
          type="submit"
          className="button button--primary"
          disabled={!allAnswered}
        >
          Submit answers
        </button>
      ) : (
        <div className={styles.result}>
          <p>
            Score: <strong>{score} / {questions.length}</strong>
            {best !== null && (
              <span className={styles.best}>
                {" "}
                — best: {best} / {questions.length}
              </span>
            )}
          </p>
          <button type="button" className="button button--secondary" onClick={handleRetry}>
            Try again
          </button>
        </div>
      )}
    </form>
  );
}
