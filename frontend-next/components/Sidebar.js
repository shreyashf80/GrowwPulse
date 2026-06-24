'use client';
import styles from './Sidebar.module.css';

const NAV_LINKS = [
  { id: 'pulse',    icon: 'dashboard',     label: 'Dashboard',       tab: true },
  { id: 'explorer', icon: 'manage_search', label: 'Review Explorer', tab: true },
  { id: 'analytics',icon: 'query_stats',   label: 'Analytics',       disabled: true },
  { id: 'sentiment',icon: 'mood',          label: 'Sentiment',       disabled: true },
  { id: 'history',  icon: 'history',       label: 'History',         disabled: true },
];

export default function Sidebar({ activeTab, onTabChange, onGenerateReport, isGenerating }) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.header}>
        <h2>Groww Pulse</h2>
        <p>Fintech Analytics</p>
      </div>

      <nav className={styles.nav}>
        {NAV_LINKS.map(link => (
          <button
            key={link.id}
            className={`${styles.link} ${!link.disabled && activeTab === link.id ? styles.active : ''} ${link.disabled ? styles.disabled : ''}`}
            onClick={() => !link.disabled && link.tab && onTabChange(link.id)}
            disabled={link.disabled}
            aria-label={link.label}
          >
            <span className="material-symbols-outlined">{link.icon}</span>
            {link.label}
          </button>
        ))}
      </nav>

      <div className={styles.cta}>
        <button
          className={`${styles.generateBtn} ${isGenerating ? styles.generating : ''}`}
          onClick={onGenerateReport}
          disabled={isGenerating}
        >
          {isGenerating ? (
            <>
              <span className={styles.spinner} />
              Generating…
            </>
          ) : (
            <>
              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>refresh</span>
              Regenerate Report
            </>
          )}
        </button>
      </div>

      <div className={styles.footer}>
        <button className={styles.link} style={{ fontSize: 13, gap: 6 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>help_outline</span>
          Support
        </button>
        <button className={styles.link} style={{ fontSize: 13, gap: 6 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>settings</span>
          Settings
        </button>
      </div>
    </aside>
  );
}
