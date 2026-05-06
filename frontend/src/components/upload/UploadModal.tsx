import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import DropZone from "./DropZone";
import ProgressSteps from "./ProgressSteps";
import SuccessSummary from "./SuccessSummary";
import { uploadDataset, type UploadProgress } from "../../services/api";
import type { Dataset } from "../../types/dataset";

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type UploadState = "idle" | "uploading" | "success" | "error";

export default function UploadModal({ isOpen, onClose }: UploadModalProps) {
  const navigate = useNavigate();
  const [state, setState] = useState<UploadState>("idle");
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [progress, setProgress] = useState<UploadProgress>({ stage: "", progress: 0 });
  const [result, setResult] = useState<Dataset | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((selectedFile: File) => {
    setFile(selectedFile);
    setName(selectedFile.name.replace(/\.[^/.]+$/, "")); // Remove extension
    setError(null);
  }, []);

  const handleUpload = useCallback(async () => {
    if (!file) return;

    setState("uploading");
    setError(null);

    try {
      const dataset = await uploadDataset(
        file,
        { name: name || undefined, description: description || undefined },
        (p) => setProgress(p)
      );
      setResult(dataset);
      setState("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
      setState("error");
    }
  }, [file, name, description]);

  const handleClose = useCallback(() => {
    setState("idle");
    setFile(null);
    setName("");
    setDescription("");
    setProgress({ stage: "", progress: 0 });
    setResult(null);
    setError(null);
    onClose();
  }, [onClose]);

  const handleViewDataset = useCallback(() => {
    if (result) {
      navigate(`/datasets/${result.id}`);
      handleClose();
    }
  }, [result, navigate, handleClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={state === "idle" ? handleClose : undefined}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              {state === "success" ? "Upload Complete" : "Upload Dataset"}
            </h2>
            {state === "idle" && (
              <button
                onClick={handleClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          {/* Content */}
          <div className="p-6">
            {state === "idle" && (
              <div className="space-y-4">
                <DropZone onFileSelect={handleFileSelect} selectedFile={file} />

                {file && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Name (optional)
                      </label>
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Dataset name"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description (optional)
                      </label>
                      <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Brief description of the dataset"
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
                      />
                    </div>
                  </>
                )}

                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                    {error}
                  </div>
                )}
              </div>
            )}

            {state === "uploading" && (
              <ProgressSteps currentStage={progress.stage} progress={progress.progress} />
            )}

            {state === "success" && result && (
              <SuccessSummary dataset={result} onViewDataset={handleViewDataset} />
            )}

            {state === "error" && (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Failed</h3>
                <p className="text-gray-600 mb-4">{error}</p>
                <button
                  onClick={() => setState("idle")}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>

          {/* Footer */}
          {state === "idle" && (
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={handleClose}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={!file}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Upload & Process
              </button>
            </div>
          )}

          {state === "success" && (
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={handleClose}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Close
              </button>
              <button
                onClick={handleViewDataset}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Dataset
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
