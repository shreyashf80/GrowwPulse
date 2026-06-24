'use client';
import { useEffect, useRef } from 'react';
import styles from './EmailPreviewModal.module.css';

export default function EmailPreviewModal({ email, onClose }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const el = dialogRef.current;
    if (el && !el.open) el.showModal();
  }, []);

  const handleBackdropClick = (e) => {
    const rect = dialogRef.current.getBoundingClientRect();
    const isOutside =
      e.clientX < rect.left ||
      e.clientX > rect.right ||
      e.clientY < rect.top ||
      e.clientY > rect.bottom;
    if (isOutside) onClose();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(email.text_body || '');
  };

  return (
    <dialog ref={dialogRef} className={styles.dialog} onClick={handleBackdropClick}>
      <div className={styles.inner} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <span className="material-symbols-outlined" style={{ color: 'var(--color-primary)', fontSize: 22 }}>mail</span>
            <h2 className={styles.title}>Email Draft Preview</h2>
          </div>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Subject line */}
        <div className={styles.subject}>
          <span className={styles.metaLabel}>Subject</span>
          <span className={styles.metaValue}>{email.subject || '—'}</span>
        </div>

        {/* Doc link */}
        {email.doc_link && (
          <div className={styles.subject} style={{ borderTopLeftRadius: 0, borderTopRightRadius: 0, borderTop: 'none', marginTop: 0 }}>
            <span className={styles.metaLabel}>Report Link</span>
            <a
              href={email.doc_link}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.docLink}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 14 }}>open_in_new</span>
              Open Google Doc
            </a>
          </div>
        )}

        {/* Body */}
        <div className={styles.bodySection}>
          <div className={styles.bodyHeader}>
            <span className={styles.metaLabel}>Email Body (Plain Text)</span>
            <button className={styles.copyBtn} onClick={handleCopy}>
              <span className="material-symbols-outlined" style={{ fontSize: 14 }}>content_copy</span>
              Copy
            </button>
          </div>
          <pre className={styles.body}>{email.text_body || 'No email content available.'}</pre>
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <span className={styles.footerNote}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--color-on-surface-muted)' }}>info</span>
            This is a dry-run preview. Actual delivery requires running without <code>--dry-run</code>.
          </span>
          <button className={styles.closeAction} onClick={onClose}>Close</button>
        </div>
      </div>
    </dialog>
  );
}
