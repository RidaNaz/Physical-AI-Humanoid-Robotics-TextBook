/**
 * Loading indicator (typing animation)
 */

import React from 'react';
import styles from './styles.module.css';

export function LoadingIndicator() {
  return (
    <div className={styles.loadingIndicator}>
      <div className={styles.typingDot}></div>
      <div className={styles.typingDot}></div>
      <div className={styles.typingDot}></div>
    </div>
  );
}
