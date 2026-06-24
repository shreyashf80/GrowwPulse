'use client';
import { useState } from 'react';
import styles from './ThemeCard.module.css';

function ratingClass(avg) {
  if (avg >= 3.5) return 'green';
  if (avg >= 2.5) return 'amber';
  return 'red';
}

function quoteBorderColor(rating) {
  if (rating >= 4) return 'green';
  if (rating <= 2) return 'red';
  return 'amber';
}

export default function ThemeCard({ theme, rank, totalReviews, isWide }) {
  const [actionsOpen, setActionsOpen] = useState(false);
  const cls       = ratingClass(theme.avg_rating);
  const pct       = ((theme.review_count / totalReviews) * 100).toFixed(1);
  const barColor  = cls === 'green' ? 'var(--color-primary)' : cls === 'amber' ? 'var(--color-secondary-container)' : 'var(--color-error)';

  return (
    <div className={`glass-card ${styles.card} ${isWide ? styles.wide : ''}`}>
      {/* Top row */}
      <div className={styles.top}>
        <div className={styles.rankName}>
          <span className={`${styles.rankBadge} ${styles['rank' + cls]}`}>{rank}</span>
          <div>
            <h3 className={styles.name}>{theme.theme_name}</h3>
            <p className={styles.desc}>{theme.description}</p>
          </div>
        </div>
        <div className={styles.right}>
          <span className={`${styles.ratingPill} ${styles[cls]}`}>
            <span className="material-symbols-outlined icon-filled" style={{ fontSize: 13 }}>star</span>
            {theme.avg_rating} ★
          </span>
          <span className={styles.reviewCount}>{theme.review_count} reviews</span>
        </div>
      </div>

      {/* Quotes */}
      <div className={styles.quotes}>
        {(theme.quotes || []).slice(0, 3).map((q, i) => (
          <div key={i} className={styles.quoteItem}>
            <div className={`${styles.quoteBorder} ${styles[quoteBorderColor(q.rating)]}`} />
            <span className={styles.quoteText}>"{q.text}"</span>
          </div>
        ))}
      </div>

      {/* Action Ideas collapsible */}
      <div>
        <button
          className={`${styles.actionToggle} ${actionsOpen ? styles.open : ''}`}
          onClick={() => setActionsOpen(o => !o)}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>expand_more</span>
          ACTION IDEAS
        </button>
        {actionsOpen && (
          <div className={styles.actionsBody}>
            {(theme.action_ideas || []).map((a, i) => (
              <div key={i} className={styles.actionItem}>
                <strong>{a.title}:</strong>&nbsp;{a.detail}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div className={styles.progressTrack}>
        <div
          className={styles.progressFill}
          style={{ width: `${pct}%`, background: barColor }}
          title={`${pct}% of all reviews`}
        />
      </div>
    </div>
  );
}
