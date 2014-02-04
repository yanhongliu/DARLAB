#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <errno.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifdef __APPLE__
#define GLOBAL_DIRECTIVE ".globl"
#define SYMBOL_PREFIX "_"
#else
#define GLOBAL_DIRECTIVE ".global"
#define SYMBOL_PREFIX ""
#endif

const char* const opts = "o:";

static void usage(void) __attribute__ ((noreturn));

static void usage()
{
	printf("Usage: py2s -o [outfile] [infile]\n");

	exit(-1);
}

static int fdprintf(int fd, const char* format, ...)
{
	va_list ap;

	char tmp;
	int len;
	char* buf;

	va_start(ap, format);
	len = vsnprintf(&tmp, 0, format, ap);
	va_end(ap);

	buf = alloca(len + 1); 

	va_start(ap, format);
	vsnprintf(buf, len + 1, format, ap);
	va_end(ap);

	write(fd, buf, len);

	return len;
}

static char* var_from_path(char* path)
{
	off_t i;

	char* file = strrchr(path, '/');

	if(file)
		file = strdup(file + 1);
	else
		file = path;

	size_t filelen = strlen(file);

	for(i = 0; i < filelen; i++) {
		if((file[i] >= 'a' && file[i] <= 'z') ||
		   (file[i] >= 'A' && file[i] <= 'Z') ||
		   (file[i] >= '1' && file[i] <= '9') ||
		   (file[i] == '0' || file[i] == '_'))
			continue;

		file[i] = '_';
	}

	return file;
}

static void py2s(char* outfile, char* infile)
{
	int out_fd;
	int in_fd;
	struct stat in_stat;
	char* in_map;
	off_t in_pos;

	out_fd = open(outfile, O_WRONLY | O_CREAT, 0644);
	
	if(out_fd == -1) {
		printf("Couldn't open %s: %s\n", outfile, strerror(errno));
		exit(-1);
	}

	in_fd = open(infile, O_RDONLY);

	if(in_fd == -1) {
		printf("Couldn't open %s: %s\n", infile, strerror(errno));
		close(out_fd);
		exit(-1);
	}

	if(fstat(in_fd, &in_stat) == -1) {
		printf("Couldn't stat %s: %s\n", infile, strerror(errno));
		close(in_fd);
		close(out_fd);
		exit(-1);
	}

	if(in_stat.st_size == 0)
	{
		printf("Input file must have nonzero length.\n");
		close(in_fd);
		close(out_fd);
		exit(-1);
	}

	if((in_map = mmap(NULL, in_stat.st_size, PROT_READ, MAP_PRIVATE, in_fd, 0)) == (void*)-1) {
		printf("Couldn't mmap %s: %s\n", infile, strerror(errno));
		close(in_fd);
		close(out_fd);
		exit(-1);
	}

	ftruncate(out_fd, 0);

	fdprintf(out_fd, ".text\n");
	fdprintf(out_fd, "%s %s%s\n", GLOBAL_DIRECTIVE, SYMBOL_PREFIX, var_from_path(infile));
	fdprintf(out_fd, "%s%s:\n", SYMBOL_PREFIX, var_from_path(infile));
	fdprintf(out_fd, ".asciz \"");

	for(in_pos = 0; in_pos < in_stat.st_size; in_pos++) {
		char cur_char = *((char*)in_map + in_pos);

		switch(cur_char) {
		case '\b':
			fdprintf(out_fd, "\\b");
			break;
		case '\f':
			fdprintf(out_fd, "\\f");
			break;
		case '\n':
			fdprintf(out_fd, "\\n");
			break;
		case '\r':
			fdprintf(out_fd, "\\r");
			break;
		case '\t':
			fdprintf(out_fd, "\\t");
			break;
		case '\\':
			fdprintf(out_fd, "\\\\");
			break;
		case '\"':
			fdprintf(out_fd, "\\\"");
			break;
		default:
			write(out_fd, &cur_char, 1);
			break;
		}
	}

	fdprintf(out_fd, "\"\n");

	munmap(in_map, in_stat.st_size);
	close(out_fd);
	close(in_fd);
}

int main(int argc, char* const argv[])
{
	char curopt;

	char* infile = NULL;
	char* outfile = NULL;

	while((curopt = getopt(argc, argv, opts)) != -1) {
		switch(curopt) {
		case 'o':
			outfile = strdup(optarg);
			break;
		default:
			usage();
		}
	}

	if(!outfile)
		usage();

	if(!argv[optind])
		usage();

	infile = strdup(argv[optind]);

	py2s(outfile, infile);

	free(outfile);
	free(infile);

	exit(0);
}
