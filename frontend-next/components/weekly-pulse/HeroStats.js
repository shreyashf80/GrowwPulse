import styles from './HeroStats.module.css';

function ratingClass(avg) {
  if (avg >= 3.5) return styles.green;
  if (avg >= 2.5) return styles.amber;
  return styles.red;
}

const DOT_COLORS = ['#3fe56c', '#93000a', '#3fe56c', '#93000a', '#ff8f00'];

export default function HeroStats({ data }) {
  const avgClass = ratingClass(data.avg_rating);

  return (
    <div className={styles.grid}>
      {/* Reviews Ingested */}
      <div className={`glass-card ${styles.card}`}>
        <span className={styles.label}>Reviews Ingested</span>
        <span className={styles.value}>
          {data.reviews_ingested.toLocaleString()}
          <span className={styles.delta}>+12%</span>
        </span>
        <span className={styles.sub}>{data.window_weeks}-week window</span>
      </div>

      {/* Themes Identified */}
      <div className={`glass-card ${styles.card}`}>
        <span className={styles.label}>Themes Identified</span>
        <span className={styles.value}>{data.themes.length}</span>
        <div className={styles.dots}>
          {data.themes.map((_, i) => (
            <span
              key={i}
              className={styles.dot}
              style={{ background: DOT_COLORS[i] || '#bbcbb8' }}
            />
          ))}
        </div>
      </div>

      {/* Avg Rating */}
      <div className={`glass-card ${styles.card}`}>
        <span className={styles.label}>Avg Rating</span>
        <div className={`${styles.ratingRow} ${avgClass}`}>
          {data.avg_rating}
          <span className="material-symbols-outlined icon-filled" style={{ fontSize: 28 }}>star</span>
          <span className={styles.criticalBadge}>Critical Volume</span>
        </div>
        <span className={styles.sub}>{data.iso_week}</span>
      </div>

      {/* LLM Tokens */}
      <div className={`glass-card ${styles.card}`}>
        <span className={styles.label}>LLM Tokens</span>
        <span className={styles.value}>
          {data.pipeline?.llm_tokens_used?.toLocaleString() || 0} 
          <span style={{ fontSize: '16px', color: 'var(--color-on-surface-muted)', fontWeight: 500 }}>
            / {((data.pipeline?.llm_tokens_limit || 100000) / 1000).toLocaleString()}K
          </span>
        </span>
        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill} 
            style={{ width: `${Math.min(100, ((data.pipeline?.llm_tokens_used || 0) / (data.pipeline?.llm_tokens_limit || 100000)) * 100)}%` }}
          />
        </div>
        <span className={styles.sub}>Quota refreshes in 4d</span>
      </div>
    </div>
  );
}
