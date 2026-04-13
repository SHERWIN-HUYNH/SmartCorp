'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { AlertCircle, File, FileText, RefreshCw, X } from 'lucide-react';

import { getProcessingQueue, type ProcessingQueueItem } from '@/lib/auth-api';

type QueueFileType = 'pdf' | 'docx' | 'txt' | 'md' | 'other';
type QueueVisualTone = 'primary' | 'error';

interface QueueItemData {
  id: string;
  name: string;
  size: string;
  progress: number;
  statusLabel: string;
  type: QueueFileType;
  tone: QueueVisualTone;
  activeSteps: string[];
  errorMessage?: string;
}

function formatFileSize(bytes?: number | null): string {
  if (!bytes || bytes <= 0) {
    return 'Unknown size';
  }

  const units = ['B', 'KB', 'MB', 'GB'];
  let value = bytes;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }

  const rounded = value >= 10 ? value.toFixed(0) : value.toFixed(1);
  return `${rounded} ${units[unitIndex]}`;
}

function resolveFileType(filename: string, mimeType?: string | null): QueueFileType {
  if (mimeType?.includes('pdf') || filename.toLowerCase().endsWith('.pdf')) {
    return 'pdf';
  }
  if (
    mimeType?.includes('word') ||
    filename.toLowerCase().endsWith('.docx') ||
    filename.toLowerCase().endsWith('.doc')
  ) {
    return 'docx';
  }
  if (mimeType?.includes('text/plain') || filename.toLowerCase().endsWith('.txt')) {
    return 'txt';
  }
  if (mimeType?.includes('markdown') || filename.toLowerCase().endsWith('.md')) {
    return 'md';
  }
  return 'other';
}

function mapQueueItem(item: ProcessingQueueItem): QueueItemData {
  if (item.status === 'pending') {
    return {
      id: item.id,
      name: item.filename,
      size: formatFileSize(item.file_size_bytes),
      progress: 20,
      statusLabel: 'Queued',
      type: resolveFileType(item.filename, item.mime_type),
      tone: 'primary',
      activeSteps: ['uploading'],
    };
  }

  if (item.status === 'failed') {
    return {
      id: item.id,
      name: item.filename,
      size: formatFileSize(item.file_size_bytes),
      progress: 100,
      statusLabel: 'Failed',
      type: resolveFileType(item.filename, item.mime_type),
      tone: 'error',
      activeSteps: ['uploading', 'failed'],
      errorMessage: item.error_message || undefined,
    };
  }

  return {
    id: item.id,
    name: item.filename,
    size: formatFileSize(item.file_size_bytes),
    progress: 70,
    statusLabel: 'Processing',
    type: resolveFileType(item.filename, item.mime_type),
    tone: 'primary',
    activeSteps: ['uploading', 'parsing', 'chunking', 'embedding'],
  };
}

export function ProcessingQueue() {
  const [queueItems, setQueueItems] = useState<QueueItemData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadQueue = useCallback(async (silent = false) => {
    if (!silent) {
      setLoading(true);
    }

    setError(null);

    try {
      const queue = await getProcessingQueue();
      setQueueItems(queue.items.map(mapQueueItem));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load processing queue.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadQueue();

    const pollingTimer = window.setInterval(() => {
      void loadQueue(true);
    }, 8000);

    return () => window.clearInterval(pollingTimer);
  }, [loadQueue]);

  const handleRefresh = () => {
    setRefreshing(true);
    void loadQueue(true);
  };

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-headline font-bold text-on-surface flex items-center gap-2">
          <RefreshCw className="text-primary w-5 h-5" />
          Active Processing Queue
        </h3>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleRefresh}
            className="p-2 rounded-lg border border-outline-variant/20 text-outline hover:text-primary hover:border-primary/40 transition-colors"
            aria-label="Refresh processing queue"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-primary' : ''}`} />
          </button>
          <span className="text-xs font-bold px-2 py-1 bg-secondary-container text-on-secondary-container rounded-lg">
            {queueItems.length} active threads
          </span>
        </div>
      </div>

      <div className="bg-surface-container-lowest rounded-2xl overflow-hidden shadow-sm border border-outline-variant/10">
        {loading && (
          <div className="p-6 text-sm text-outline">Loading processing queue...</div>
        )}

        {!loading && error && (
          <div className="p-6 flex items-start gap-3 text-sm text-error">
            <AlertCircle className="w-5 h-5 mt-0.5" />
            <div>
              <p className="font-semibold">Unable to load queue</p>
              <p className="text-on-surface-variant mt-1">{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && queueItems.length === 0 && (
          <div className="p-6 text-sm text-outline">
            No files are currently being processed.
          </div>
        )}

        {!loading && !error && queueItems.map((item, index) => (
          <div
            key={item.id}
            className={`p-4 flex items-center gap-6 ${index !== queueItems.length - 1 ? 'border-b border-outline-variant/5' : ''}`}
          >
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${item.type === 'pdf' ? 'bg-error-container/20 text-error' : 'bg-primary-fixed text-primary'}`}>
              {item.type === 'pdf' ? <FileText className="w-5 h-5" /> : <File className="w-5 h-5" />}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="font-bold text-sm truncate">{item.name}</span>
                  <span className="text-xs text-outline font-medium whitespace-nowrap">{item.size}</span>
                </div>
                <span className={`text-xs font-bold tracking-wide uppercase ${item.tone === 'error' ? 'text-error' : 'text-primary'}`}>
                  {item.progress}% {item.statusLabel}
                </span>
              </div>

              <div className="w-full bg-surface-container-high rounded-full h-2 overflow-hidden">
                <div
                  className={`${item.tone === 'error' ? 'bg-error' : 'bg-primary'} h-full rounded-full transition-all duration-500`}
                  style={{ width: `${item.progress}%` }}
                ></div>
              </div>

              <div className="flex items-center gap-4 mt-3">
                {item.activeSteps.map((step, i) => {
                  const isCurrent = i === item.activeSteps.length - 1;
                  const stepTextClass = isCurrent
                    ? item.tone === 'error'
                      ? 'text-error'
                      : 'text-outline'
                    : 'text-primary';
                  const stepDotClass = isCurrent
                    ? item.tone === 'error'
                      ? 'bg-error'
                      : 'bg-outline'
                    : 'bg-primary';

                  return (
                    <span key={`${item.id}-${step}`} className={`flex items-center gap-1 text-[10px] font-bold uppercase ${stepTextClass}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${stepDotClass}`}></span>
                      {step}
                    </span>
                  );
                })}
              </div>

              {item.errorMessage && (
                <p className="mt-2 text-xs text-error truncate" title={item.errorMessage}>
                  {item.errorMessage}
                </p>
              )}
            </div>

            <button
              type="button"
              disabled
              className="p-2 text-outline/40 rounded-full cursor-not-allowed"
              title="Cancellation is not available yet"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
