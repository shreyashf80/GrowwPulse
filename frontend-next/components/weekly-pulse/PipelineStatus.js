'use client';
import styles from './PipelineStatus.module.css';

export default function PipelineStatus({ pipeline, email, onPreviewEmail }) {
  const docUrl = pipeline.doc_url;

  const badges = [
    {
      icon: 'description',
      label: 'Google Docs',
      value: pipeline.doc_status === 'appended' ? 'Appended' : pipeline.doc_status,
      action: docUrl
        ? { label: 'Open Doc', icon: 'open_in_new', href: docUrl }
        : null,
    },
    {
      icon: 'mail',
      label: 'Gmail',
      value: pipeline.gmail_status === 'draft_created' ? 'Draft Created' : pipeline.gmail_status,
      action: email?.text_body
        ? { label: 'Preview Draft', icon: 'visibility', onClick: onPreviewEmail }
        : null,
    },
    { icon: 'tag',       label: 'Run ID', value: pipeline.run_id },
    { icon: 'smart_toy', label: 'Model',  value: pipeline.model },
  ];

  return (
    <div className={styles.bar}>
      <span className={styles.barLabel}>
        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>settings</span>
        Pipeline Execution Status
      </span>

      {badges.map((b) => (
        <span key={b.label} className={styles.badge}>
          <span
            className="material-symbols-outlined"
            style={{ fontSize: 16, color: 'var(--color-primary)' }}
          >
            {b.icon}
          </span>
          {b.label}: <strong>{b.value}</strong>

          {b.action?.href && (
            <a
              href={b.action.href}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.actionLink}
              title={b.action.label}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 13 }}>{b.action.icon}</span>
              {b.action.label}
            </a>
          )}
          {b.action?.onClick && (
            <button
              className={styles.actionLink}
              onClick={b.action.onClick}
              title={b.action.label}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 13 }}>{b.action.icon}</span>
              {b.action.label}
            </button>
          )}
        </span>
      ))}
    </div>
  );
}
