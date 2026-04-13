'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { UploadCloud, X, ChevronDown } from 'lucide-react';
import { listRoles, RoleOption, uploadDocuments } from '@/lib/auth-api';

const ACCEPTED_EXTENSIONS = ['pdf', 'docx', 'json', 'md'];

function getFileExtension(fileName: string) {
  const parts = fileName.split('.');
  return parts.length > 1 ? parts.pop()!.toLowerCase() : '';
}

function formatFileSize(size: number) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

export function UploadSection() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [effectiveDate, setEffectiveDate] = useState('');
  const [availableRoles, setAvailableRoles] = useState<RoleOption[]>([]);
  const [selectedRoleIds, setSelectedRoleIds] = useState<string[]>([]);
  const [isRolesLoading, setIsRolesLoading] = useState(true);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadRoles() {
      setIsRolesLoading(true);
      try {
        const roles = await listRoles();
        if (!mounted) {
          return;
        }
        setAvailableRoles(roles);

        const adminRole = roles.find((role) => role.name.toLowerCase() === 'admin');
        const defaultRoleId = adminRole?.id || roles[0]?.id;
        setSelectedRoleIds(defaultRoleId ? [defaultRoleId] : []);
      } catch (error) {
        if (!mounted) {
          return;
        }
        const message = error instanceof Error ? error.message : 'Failed to load roles.';
        setSubmitError(message);
      } finally {
        if (mounted) {
          setIsRolesLoading(false);
        }
      }
    }

    loadRoles();
    return () => {
      mounted = false;
    };
  }, []);

  const getRoleName = (roleId: string) => {
    const role = availableRoles.find((item) => item.id === roleId);
    return role?.name || roleId;
  };

  const canSubmit = useMemo(() => {
    return (
      files.length > 0 &&
      effectiveDate.length > 0 &&
      selectedRoleIds.length > 0 &&
      !isRolesLoading &&
      !isSubmitting
    );
  }, [files.length, effectiveDate, selectedRoleIds.length, isRolesLoading, isSubmitting]);

  const resetForm = () => {
    setFiles([]);
    setEffectiveDate('');
    const adminRole = availableRoles.find((role) => role.name.toLowerCase() === 'admin');
    const defaultRoleId = adminRole?.id || availableRoles[0]?.id;
    setSelectedRoleIds(defaultRoleId ? [defaultRoleId] : []);
    setIsDropdownOpen(false);
  };

  const validateAndMergeFiles = (incomingFiles: FileList | File[]) => {
    const incoming = Array.from(incomingFiles);

    if (incoming.length === 0) {
      return;
    }

    const accepted: File[] = [];
    const rejectedReasons: string[] = [];

    incoming.forEach((file) => {
      const extension = getFileExtension(file.name);
      if (!ACCEPTED_EXTENSIONS.includes(extension)) {
        rejectedReasons.push(`${file.name}: unsupported format`);
        return;
      }

      accepted.push(file);
    });

    setFiles((prev) => {
      const next = [...prev];
      accepted.forEach((file) => {
        const duplicate = next.some(
          (existing) =>
            existing.name === file.name &&
            existing.size === file.size &&
            existing.lastModified === file.lastModified
        );
        if (!duplicate) {
          next.push(file);
        }
      });
      return next;
    });

    if (rejectedReasons.length > 0) {
      setSubmitError(`Some files were not added: ${rejectedReasons.join('; ')}`);
      setSubmitSuccess(null);
      return;
    }

    setSubmitError(null);
    setSubmitSuccess(null);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;
    validateAndMergeFiles(event.target.files);
    event.target.value = '';
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    validateAndMergeFiles(event.dataTransfer.files);
  };

  const removeFile = (targetFile: File) => {
    setFiles((prev) =>
      prev.filter(
        (file) =>
          !(
            file.name === targetFile.name &&
            file.size === targetFile.size &&
            file.lastModified === targetFile.lastModified
          )
      )
    );
  };

  const clearFiles = () => {
    setFiles([]);
  };

  const handleSubmit = async () => {
    setSubmitError(null);
    setSubmitSuccess(null);

    if (files.length === 0) {
      setSubmitError('Please add at least one valid file.');
      return;
    }
    if (!effectiveDate) {
      setSubmitError('Effective date is required.');
      return;
    }
    if (selectedRoleIds.length === 0) {
      setSubmitError('Please select at least one role.');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await uploadDocuments({
        files,
        effectiveDate,
        roleIds: selectedRoleIds,
      });

      if (result.uploaded > 0) {
        setSubmitSuccess(result.message);
        resetForm();
      } else {
        setSubmitError(result.items.map((item) => `${item.filename}: ${item.detail}`).join(' | '));
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Upload failed. Please try again.';
      setSubmitError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleRole = (roleId: string) => {
    setSelectedRoleIds((prev) =>
      prev.includes(roleId) ? prev.filter((id) => id !== roleId) : [...prev, roleId]
    );
  };

  const removeRole = (roleId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedRoleIds((prev) => prev.filter((id) => id !== roleId));
  };

  return (
    <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
      {/* Drag & Drop */}
      <div
        onClick={handleBrowseClick}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            handleBrowseClick();
          }
        }}
        className="lg:col-span-5 bg-surface-container-lowest border-2 border-dashed border-outline-variant rounded-2xl p-8 flex flex-col items-center justify-center gap-4 group hover:bg-primary-fixed/5 transition-all cursor-pointer"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.json,.md"
          onChange={handleFileInputChange}
          className="hidden"
        />
        <div className="w-16 h-16 rounded-full bg-primary-fixed flex items-center justify-center text-on-primary-fixed transition-transform group-hover:scale-110">
          <UploadCloud className="w-8 h-8" />
        </div>
        <div className="text-center">
          <h3 className="font-headline font-bold text-lg">Drag & Drop Zone</h3>
          <p className="text-sm text-on-surface-variant px-4 mt-1">
            Supported formats: PDF, DOCX, JSON, MD.
          </p>
        </div>
        <button
          type="button"
          onClick={handleBrowseClick}
          className="mt-2 text-primary text-sm font-bold border-b-2 border-primary/20 hover:border-primary transition-all"
        >
          Browse local storage
        </button>

        {files.length > 0 && (
          <div className="w-full mt-3 rounded-xl bg-surface-container-high p-3">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-bold uppercase tracking-wide text-outline">Selected Files ({files.length})</p>
              <button
                type="button"
                onClick={clearFiles}
                className="text-xs font-semibold text-primary hover:opacity-80"
              >
                Clear all
              </button>
            </div>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {files.map((file) => (
                <div key={`${file.name}-${file.lastModified}-${file.size}`} className="flex items-center justify-between gap-2 rounded-lg bg-surface-container px-3 py-2">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{file.name}</p>
                    <p className="text-xs text-on-surface-variant">{formatFileSize(file.size)}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeFile(file)}
                    className="text-outline hover:text-on-surface transition-colors"
                    aria-label={`Remove ${file.name}`}
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Metadata Form */}
      <div className="lg:col-span-7 bg-surface-container-lowest rounded-2xl p-8 shadow-sm border border-outline-variant/10 flex flex-col justify-between">
        <div className="grid grid-cols-1 gap-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-outline uppercase tracking-wider">Effective Date</label>
            <input 
              value={effectiveDate}
              onChange={(event) => setEffectiveDate(event.target.value)}
              className="w-full bg-surface-container border-none rounded-xl text-sm py-2 px-4 focus:ring-2 focus:ring-primary/5 focus:outline-none" 
              type="date" 
            />
          </div>
        </div>

        {/* Role Access Multi-Selection */}
        <div className="mt-4 space-y-2">
          <label className="text-xs font-bold text-outline uppercase tracking-wider">Role Access</label>
          <div className="relative">
            <div 
              className="w-full bg-surface-container border border-transparent rounded-xl p-2 flex flex-wrap gap-2 items-start content-start min-h-[44px] max-h-[88px] overflow-y-auto focus-within:ring-2 focus-within:ring-primary/10 transition-all cursor-pointer"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              {selectedRoleIds.map((roleId) => (
                <span key={roleId} className="flex items-center gap-1 px-3 py-1 bg-primary text-white text-xs font-bold rounded-lg shrink-0">
                  {getRoleName(roleId)}
                  <X className="w-3 h-3 cursor-pointer hover:text-white/80" onClick={(e) => removeRole(roleId, e)} />
                </span>
              ))}
              {selectedRoleIds.length === 0 && <span className="text-outline text-sm ml-1 mt-0.5">Select roles...</span>}
              <ChevronDown className="w-4 h-4 ml-auto mt-1 text-outline shrink-0" />
            </div>

            {/* Dropdown */}
            {isDropdownOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setIsDropdownOpen(false)}></div>
                <div className="absolute top-full left-0 w-full mt-2 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="p-1 max-h-48 overflow-y-auto">
                    {availableRoles.map((role) => (
                      <label key={role.id} className="px-4 py-2 hover:bg-slate-50 text-sm font-medium flex items-center gap-3 text-on-surface cursor-pointer rounded-lg">
                        <input 
                          type="checkbox" 
                          checked={selectedRoleIds.includes(role.id)}
                          onChange={() => toggleRole(role.id)}
                          className="rounded border-slate-300 text-primary focus:ring-primary w-4 h-4" 
                        />
                        {role.name}
                      </label>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-end gap-4">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="w-full sm:w-auto bg-primary-container text-white px-8 py-3 rounded-xl font-bold text-sm shadow-xl shadow-primary-container/20 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {isSubmitting ? 'Uploading...' : isRolesLoading ? 'Loading roles...' : 'Upload & Process All'}
          </button>
        </div>

        {submitError && (
          <p className="mt-4 text-sm font-medium text-red-600">{submitError}</p>
        )}
        {submitSuccess && (
          <p className="mt-4 text-sm font-medium text-emerald-600">{submitSuccess}</p>
        )}
      </div>
    </section>
  );
}
