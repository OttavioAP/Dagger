import Image from "next/image";

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
      <footer className="mt-16 text-gray-400 text-sm text-center">
        &copy; {new Date().getFullYear()} Dagger Productivity. All rights reserved.
      </footer>
    </div>
  );
}
