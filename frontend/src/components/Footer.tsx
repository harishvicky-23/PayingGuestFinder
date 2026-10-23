import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ShieldCheck, Cpu, MapPin } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 text-sm mt-auto border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Info */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center text-white font-bold">
                <Home className="w-4 h-4" />
              </div>
              <span className="text-white text-lg font-bold">StayNearby</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              Find the right space, for exactly as long as you need. A two-sided short-duration rental marketplace powered by explainable ML recommendation and demand forecasting.
            </p>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 text-brand-400 text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Simulated Demo Environment</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-3 text-xs uppercase tracking-wider">Marketplace</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/explore" className="hover:text-white transition">Explore Listings</Link></li>
              <li><Link to="/explore?type=workspace_studio" className="hover:text-white transition">Workspace Studios</Link></li>
              <li><Link to="/explore?type=private_room" className="hover:text-white transition">Day Transit Rooms</Link></li>
              <li><Link to="/explore?type=day_cabin" className="hover:text-white transition">Quiet Garden Pods</Link></li>
              <li><Link to="/explore?type=entire_apartment" className="hover:text-white transition">Entire Apartments</Link></li>
            </ul>
          </div>

          {/* Popular Chennai Areas */}
          <div>
            <h4 className="text-white font-semibold mb-3 text-xs uppercase tracking-wider">Top Hubs (Chennai)</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/explore?neighbourhood=Guindy" className="hover:text-white transition flex items-center gap-1"><MapPin className="w-3 h-3 text-brand-400" /> Guindy Metro & Tech Park</Link></li>
              <li><Link to="/explore?neighbourhood=Velachery" className="hover:text-white transition flex items-center gap-1"><MapPin className="w-3 h-3 text-brand-400" /> Velachery Mall Corridor</Link></li>
              <li><Link to="/explore?neighbourhood=T.%20Nagar" className="hover:text-white transition flex items-center gap-1"><MapPin className="w-3 h-3 text-brand-400" /> T. Nagar Retail & Commercial</Link></li>
              <li><Link to="/explore?neighbourhood=Adyar" className="hover:text-white transition flex items-center gap-1"><MapPin className="w-3 h-3 text-brand-400" /> Adyar Green Coastal Haven</Link></li>
              <li><Link to="/explore?neighbourhood=OMR" className="hover:text-white transition flex items-center gap-1"><MapPin className="w-3 h-3 text-brand-400" /> OMR IT Expressway</Link></li>
            </ul>
          </div>

          {/* MLOps & Architecture */}
          <div>
            <h4 className="text-white font-semibold mb-3 text-xs uppercase tracking-wider">MLOps & Platform</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/admin/ml-operations" className="hover:text-white transition flex items-center gap-1"><Cpu className="w-3 h-3 text-indigo-400" /> MLOps Operations</Link></li>
              <li><Link to="/host/analytics" className="hover:text-white transition">Neighbourhood Demand Forecasts</Link></li>
              <li><Link to="/host/dashboard" className="hover:text-white transition">Host Control Dashboard</Link></li>
              <li><span className="text-slate-500">MLflow Local Registry</span></li>
              <li><span className="text-slate-500">Haversine Distance Engine</span></li>
            </ul>
          </div>
        </div>

        {/* Disclaimer bar */}
        <div className="pt-6 border-t border-slate-800 text-xs text-slate-500 flex flex-col md:flex-row justify-between items-center gap-4">
          <p>
            © 2026 StayNearby Project. Built with React, FastAPI, SQLAlchemy, Scikit-learn, and MLflow.
          </p>
          <p className="text-[11px] text-slate-500 max-w-xl text-center md:text-right">
            Demonstration mode: Geographic coordinates and demand models use synthetic datasets and approximate neighbourhood centroids. Exact private residential addresses remain confidential.
          </p>
        </div>
      </div>
    </footer>
  );
};
