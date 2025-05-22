import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white px-4">
      <header className="flex flex-col items-center mb-12">
        <Image
          src="/Dagger_Logo.png"
          alt="Dagger Logo"
          width={120}
          height={120}
          className="mb-6 drop-shadow-lg rounded-full bg-white/10"
          priority
        />
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-2 text-center">
          Dagger Productivity
        </h1>
        <p className="text-lg sm:text-xl text-gray-300 max-w-2xl text-center">
          Supercharge your productivity with task management powered by Directed Acyclic Graphs. Visualize, organize, and optimize your workflow like never before.
        </p>
      </header>
      <main className="flex flex-col items-center gap-8 w-full max-w-xl">
        <div className="bg-white/5 rounded-xl p-8 shadow-lg w-full flex flex-col items-center">
          <h2 className="text-2xl font-semibold mb-4">Coming Soon</h2>
          <p className="text-gray-300 mb-6 text-center">
            Dagger is a next-generation productivity tracker that lets you break down complex projects into manageable, interconnected tasks. Stay tuned for our launch!
          </p>
          <button className="bg-gradient-to-r from-blue-500 to-teal-400 hover:from-blue-600 hover:to-teal-500 text-white font-bold py-3 px-8 rounded-full shadow transition-all duration-200">
            Get Notified
          </button>
        </div>
        <Link href="/login" className="mt-8 w-full flex justify-center">
          <span className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white font-bold py-4 px-12 rounded-full shadow-lg text-xl transition-all duration-200">
            Login
          </span>
        </Link>
      </main>
      <footer className="mt-16 text-gray-400 text-sm text-center">
        &copy; {new Date().getFullYear()} Dagger Productivity. All rights reserved.
      </footer>
    </div>
  );
}
