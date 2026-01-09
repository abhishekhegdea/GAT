import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Modal = ({ open, title, children, onClose, onConfirm, confirmText = 'Confirm' }) => {
  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="absolute inset-0 bg-black/50" onClick={onClose}></div>
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="glass max-w-lg w-full p-6 z-10"
          >
            <div className="text-white font-semibold text-lg mb-4">{title}</div>
            <div className="text-gray-200 mb-6">{children}</div>
            <div className="flex justify-end gap-3">
              <button className="btn-secondary" onClick={onClose}>Cancel</button>
              <button className="btn-primary" onClick={onConfirm}>{confirmText}</button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Modal;
