function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-blue-900">
      <div className="bg-white p-10 rounded-2xl shadow-2xl text-center border border-gray-100">
        <h1 className="text-4xl font-extrabold text-blue-900 mb-4 tracking-tight">
          प्रजा-नेत्र (Prajā-Netra)
        </h1>
        <p className="text-gray-500 text-lg">
          Frontend is now live with <span className="text-blue-600 font-mono">Tailwind + Vite</span>
        </p>
        <button className="mt-8 px-8 py-3 bg-red-600 text-white font-bold rounded-xl shadow-lg hover:bg-red-700 hover:scale-105 transition-all">
          Enter Portal
        </button>
      </div>
    </div>
  )
}

export default App