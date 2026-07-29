import React, { useState } from 'react';
import { UploadCloud, File, FileText, Sparkles, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { motion } from 'framer-motion';

export function MedicalReportViewer() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<{ text: string, explanation: string } | null>(null);

  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const analyzeFile = () => {
    setIsAnalyzing(true);
    // Mock analysis delay
    setTimeout(() => {
      setResult({
        text: "PATIENT: Ananya Sharma\nDATE: 2023-11-15\n\nTEST: Complete Blood Count\n\nHemoglobin: 13.5 g/dL (Normal: 12.0 - 15.5)\nWBC Count: 6.2 k/uL (Normal: 4.5 - 11.0)\nPlatelets: 250 k/uL (Normal: 150 - 450)\nGlucose (Fasting): 92 mg/dL (Normal: 70 - 100)",
        explanation: "Based on the report, all your key indicators are within the normal range. Your Hemoglobin, White Blood Cell count, and Platelets show healthy blood levels. Your fasting glucose is also normal, indicating good blood sugar control."
      });
      setIsAnalyzing(false);
    }, 2500);
  };

  return (
    <div className="space-y-6">
      {!file ? (
        <Card>
          <CardContent>
            <div 
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="border-2 border-dashed border-muted-foreground/25 rounded-xl p-12 mt-6 flex flex-col items-center justify-center text-center hover:bg-muted/50 transition-colors cursor-pointer"
            >
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <UploadCloud className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Upload Medical Report</h3>
              <p className="text-muted-foreground mb-6 max-w-sm">
                Drag and drop your PDF or image here, or click to browse. We'll analyze it securely.
              </p>
              <Button asChild>
                <label>
                  Browse Files
                  <input type="file" className="hidden" accept=".pdf,image/*" onChange={(e) => e.target.files && setFile(e.target.files[0])} />
                </label>
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="md:col-span-2">
            <CardContent className="p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <File className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="font-semibold">{file.name}</p>
                  <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => { setFile(null); setResult(null); }}>Remove</Button>
                {!result && (
                  <Button onClick={analyzeFile} disabled={isAnalyzing}>
                    {isAnalyzing ? (
                      <span className="flex items-center gap-2">
                        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                          <Sparkles className="w-4 h-4" />
                        </motion.div>
                        Analyzing...
                      </span>
                    ) : (
                      "Analyze with AI"
                    )}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {result && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <FileText className="w-5 h-5 text-muted-foreground" />
                    Extracted Text
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Textarea readOnly value={result.text} className="min-h-[250px] font-mono text-sm bg-muted/30 resize-none" />
                </CardContent>
              </Card>
              <Card className="border-secondary/30 bg-secondary/5">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-secondary" />
                    AI Explanation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="p-4 bg-background rounded-lg border shadow-sm h-[250px] overflow-y-auto leading-relaxed">
                    <div className="flex gap-3 mb-4 text-green-600 font-medium bg-green-50 dark:bg-green-900/20 p-3 rounded-md">
                      <CheckCircle2 className="w-5 h-5 shrink-0" />
                      Analysis complete. All key indicators are normal.
                    </div>
                    {result.explanation}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}
    </div>
  );
}
