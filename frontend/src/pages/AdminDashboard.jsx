import React, { useEffect, useState, useRef } from 'react';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import { motion } from 'framer-motion';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, registerables } from 'chart.js';
// ADD FileText TO THIS IMPORT LIST
import { Activity, ShieldAlert, CheckCircle, Loader2, FileText } from 'lucide-react';
import api from '../api/axios';

ChartJS.register(...registerables);

const AdminDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const dashboardRef = useRef(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const { data } = await api.get('/analytics/stats/summary');
        const processedData = {
          dept_stats: Object.entries(data.department_pie || {}).map(([name, count]) => ({ name, count })),
          status_stats: Object.entries(data.status_bar || {}).map(([status, count]) => ({ status, count })),
          total_active: data.total_active || 0
        };
        setSummary(processedData);
      } catch (err) {
        console.error("Fetch Error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

 const downloadPDF = async () => {
  const element = dashboardRef.current;
  if (!element) return;

  try {
    // 1. Give the browser a moment to finish Chart.js animations
    await new Promise(resolve => setTimeout(resolve, 500));

    // 2. Capture the element with refined settings
    const canvas = await html2canvas(element, {
      backgroundColor: '#050a15',
      scale: 2,
      useCORS: true,
      allowTaint: false,         // Set to false to prevent security blocks
      ignoreElements: (el) => el.tagName === 'BUTTON', // Don't include buttons in the PDF
    });

    const imgData = canvas.toDataURL('image/png', 1.0);

    // 3. Document Setup
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    const imgProps = pdf.getImageProperties(imgData);
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

    // 4. Header Bar
    pdf.setFillColor(30, 58, 138); // Navy Blue
    pdf.rect(0, 0, 210, 25, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(16);
    pdf.text("PRAJĀ-NETRA: INTERNAL AUDIT REPORT", 15, 12);
    pdf.setFontSize(8);
    pdf.text(`REPORT ID: PN-${new Date().getTime()} | DATE: ${new Date().toLocaleDateString()}`, 15, 18);

    // 5. Add Content
    pdf.addImage(imgData, 'PNG', 0, 25, pdfWidth, pdfHeight);

    // 6. Final Save
    pdf.save(`Integrity_Report_${new Date().toLocaleDateString()}.pdf`);

  } catch (error) {
    console.error("PDF Generation Detailed Error:", error);
    alert("System Error: Check if browser is blocking downloads or popups.");
  }
};

  if (loading || !summary) return (
    <div className="min-h-screen bg-[#050a15] flex items-center justify-center text-white">
      <Loader2 className="animate-spin mr-3" /> Syncing Global Data...
    </div>
  );

  return (
    <div className="min-h-screen bg-[#050a15] text-white p-10 font-sans">
      <header className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">Command Centre</h1>
          <p className="text-gray-500">Live Departmental Oversight</p>
        </div>
        <button
          onClick={downloadPDF}
          className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-2xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-emerald-900/20"
        >
          <FileText size={20} /> Generate Official Report
        </button>
      </header>

      <div ref={dashboardRef} className="space-y-12">
         <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard label="Total Active Cases" value={summary.total_active} icon={<Activity className="text-blue-400"/>} />
            <StatCard label="In Investigation" value={summary.status_stats.find(s => s.status === 'investigating')?.count || 0} icon={<ShieldAlert className="text-orange-400"/>} />
            <StatCard label="Departments Involved" value={summary.dept_stats.length} icon={<CheckCircle className="text-emerald-400"/>} />
         </div>

         <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            <div className="bg-white/[0.03] border border-white/10 p-8 rounded-[2.5rem] h-[400px]">
                <h3 className="text-lg font-bold mb-6 text-gray-400">Workload Distribution</h3>
                <Bar
                  data={{
                    labels: summary.dept_stats.map(d => d.name),
                    datasets: [{
                      label: 'Cases',
                      data: summary.dept_stats.map(d => d.count),
                      backgroundColor: '#3b82f6',
                      borderRadius: 8
                    }]
                  }}
                  options={{ maintainAspectRatio: false }}
                />
            </div>
            <div className="bg-white/[0.03] border border-white/10 p-8 rounded-[2.5rem] h-[400px]">
                <h3 className="text-lg font-bold mb-6 text-gray-400">Case Resolution Status</h3>
                <Pie
                  data={{
                    labels: summary.status_stats.map(s => s.status),
                    datasets: [{
                      data: summary.status_stats.map(s => s.count),
                      backgroundColor: ['#f59e0b', '#10b981', '#ef4444', '#3b82f6'],
                      borderWidth: 0
                    }]
                  }}
                  options={{ maintainAspectRatio: false }}
                />
            </div>
         </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, icon }) => (
  <div className="bg-white/[0.03] border border-white/10 p-6 rounded-3xl flex items-center justify-between">
    <div>
      <p className="text-[10px] font-black uppercase text-gray-500 tracking-widest">{label}</p>
      <h2 className="text-3xl font-bold mt-1 tracking-tighter">{value}</h2>
    </div>
    <div className="bg-white/5 p-4 rounded-2xl">{icon}</div>
  </div>
);

export default AdminDashboard;